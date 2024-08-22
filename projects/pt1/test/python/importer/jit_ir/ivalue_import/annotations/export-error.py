# -*- Python -*-
# This file is licensed under a pytorch-style license
# See LICENSE.pytorch for license information.

import typing

import torch
from torch_mlir.jit_ir_importer import ClassAnnotator, ModuleBuilder

# RUN: %PYTHON %s | FileCheck %s

mb = ModuleBuilder()


class TestModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self):
        return


test_module = TestModule()
recursivescriptmodule = torch.jit.script(test_module)

annotator = ClassAnnotator()
class_type = recursivescriptmodule._c._type()

try:
    annotator.exportPath(class_type, ["a"])
except Exception as e:
    # CHECK: class '__torch__.TestModule' does not have a method or attribute called 'a'
    print(e)
try:
    annotator.exportPath(class_type, [])
except Exception as e:
    # CHECK: Empty exported path. Can only export a property of a class.
    print(e)

try:
    annotator.exportPath(class_type, ["a", "b"])
except Exception as e:
    # This error is generated by PyTorch itself, so be a bit defensive about changes.
    # CHECK: __torch__.TestModule {{.*}} 'a'
    print(e)

# # TODO: Automatically handle unpacking Python class RecursiveScriptModule into the underlying ScriptModule.
mb.import_module(recursivescriptmodule._c, annotator)
mb.module.operation.print()
