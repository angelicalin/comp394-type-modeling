# -*- coding: utf-8 -*-

from java_type_checker import *
from tests.fixtures import Graphics
from tests.helpers import TypeTest
import unittest


class TestTypeChecking(TypeTest):

    def test_variables_never_have_type_errors(self):
        self.assertNoCompileErrors(
            Variable("p", Graphics.point))

    def test_literals_never_have_type_errors(self):
        self.assertNoCompileErrors(
            Variable("3.72", Type.double))

    def test_simple_method_call_passes(self):
        """
        Equivalent Java:

            Point p;

            p.getX()
        """
        self.assertNoCompileErrors(
            MethodCall(
                Variable("p", Graphics.point),
                "getX"))

    def test_flags_nonexistent_method(self):
        """
        Equivalent Java:

            Point p;

            p.getZ()
        """
        self.assertCompileError(
            NoSuchMethod,
            "Point has no method named getZ",
            MethodCall(
                Variable("p", Graphics.point),
                "getZ"))

    def test_flags_too_many_arguments(self):
        """
        Equivalent Java:

            Point p;

            p.getX(0.0, 1.0)
        """
        self.assertCompileError(
            JavaTypeError,
            "Wrong number of arguments for Point.getX(): expected 0, got 2",
            MethodCall(
                Variable("p", Graphics.point),"getX",Literal("0.0", Type.double),Literal("1.0", Type.double)))

    def test_flags_too_few_arguments(self):
        """
        Equivalent Java:

            Rectangle r;

            r.setPosition(0.0)
        """
        self.assertCompileError(
            JavaTypeError,
            "Wrong number of arguments for Rectangle.setPosition(): expected 2, got 1",
            MethodCall(
                Variable("r", Graphics.rectangle),
                "setPosition",
                Literal("0.0", Type.double)))

    def test_flags_wrong_argument_type(self):
        """
        Equivalent Java:

            Rectangle r;

            r.setPosition(0.0, true)
        """
        self.assertCompileError(
            JavaTypeError,
            "Rectangle.setPosition() expects arguments of type (double, double), but got (double, boolean)",
            MethodCall(
                Variable("rect", Graphics.rectangle),
                "setPosition",
                Literal("0.0", Type.double),
                Literal("true", Type.boolean)))

    def test_allows_subtypes_for_arguments(self):
        """
        Equivalent Java:

            Rectangle rect;
            Color red;

            rect.setFillColor(red)
        """
        self.assertNoCompileErrors(
            MethodCall(
                Variable("rect", Graphics.rectangle),
                "setFillColor",
                Variable("red", Graphics.color)))

    def test_flags_wrong_number_of_constructor_arguments(self):
        """
        Equivalent Java:

            Point p;

            new Rectangle(p)
        """
        self.assertCompileError(
            JavaTypeError,
            "Wrong number of arguments for Rectangle constructor: expected 2, got 1",
            ConstructorCall(
                Graphics.rectangle,
                Variable("p", Graphics.point)))

    def test_flags_wrong_constructor_argument_type(self):
        """
        Equivalent Java:

            Point p;

            new Rectangle(p, true)
        """
        self.assertCompileError(
            JavaTypeError,
            "Rectangle constructor expects arguments of type (Point, Size), but got (Point, boolean)",
            ConstructorCall(Graphics.rectangle, Variable("p", Graphics.point), Literal("true", Type.boolean)))

    def test_cannot_call_methods_on_primitives(self):
        """
        Equivalent Java:

            int x;

            x.hashCode()
        """
        self.assertCompileError(JavaTypeError,
            "Type int does not have methods",
            MethodCall(
                Variable("x", Type.int),
                "hashCode"))

        """
        Equivalent Java:

            new int()
        """
    def test_cannot_instantiate_primitives(self):
        self.assertCompileError(
            JavaTypeError,
            "Type int is not instantiable",
            ConstructorCall(
                Type.int))

    def test_does_not_allow_void_passed_as_argument(self):
        """
        Equivalent Java:

            Rectangle rect;
            Color red;

            rect.setFillColor(              // error here
                rect.setStrokeColor(red));  // returns void
        """
        self.assertCompileError(JavaTypeError,"Rectangle.setFillColor() expects arguments of type (Paint), but got (void)",
            MethodCall(Variable("rect", Graphics.rectangle),"setFillColor",
                       MethodCall(Variable("rect", Graphics.rectangle),"setStrokeColor",
                    Variable("red", Graphics.color))))


    def test_passes_deep_expression(self):
        """
        Equivalent Java:

            GraphicsGroup group;
            Window window;

            group.add(
                new Rectangle(
                    new Point(0, 0),
                    window.getSize());
        """
        self.assertNoCompileErrors(
            MethodCall(
                Variable("group", Graphics.graphics_group),
                "add",
                ConstructorCall(
                    Graphics.rectangle,
                    ConstructorCall(Graphics.point,
                        Literal("0.0", Type.double),
                        Literal("0.0", Type.double)),
                    MethodCall(
                        Variable("window", Graphics.window),
                        "getSize"))))

    def test_catch_wrong_name_in_deep_expression(self):
        """
        Equivalent Java:

            GraphicsGroup group;
            Window window;

            group.add(
                new Rectangle(
                    new Point(0, 0),
                    window.getFunky());  // error here
        """
        self.assertCompileError(
            NoSuchMethod,
            "Window has no method named getFunky",
            MethodCall(
                Variable("group", Graphics.graphics_group),
                "add",
                ConstructorCall(Graphics.rectangle,  ConstructorCall(Graphics.point,Literal("0.0", Type.double),Literal("0.0", Type.double)),
                    MethodCall(
                        Variable("window", Graphics.window),
                        "getFunky"))))

    def test_catch_wrong_type_in_deep_expression(self):
        """
        Equivalent Java:

            GraphicsGroup group;
            Window window;

            group.add(
                new Rectangle(
                    new Size(0, 0),   // error here
                    window.getSize());
        """
        self.assertCompileError(
            JavaTypeError,
            "Rectangle constructor expects arguments of type (Point, Size), but got (Size, Size)",
            MethodCall(
                Variable("group", Graphics.graphics_group),
                "add",
                ConstructorCall(
                    Graphics.rectangle,
                    ConstructorCall(Graphics.size,
                        Literal("0.0", Type.double),
                        Literal("0.0", Type.double)),
                    MethodCall(
                        Variable("window", Graphics.window),
                        "getSize"))))


if __name__ == '__main__':
    unittest.main()
