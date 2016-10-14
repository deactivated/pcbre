from pcbre.model.change import ChangeType
from pcbre.model.project import Project
from pcbre.model.stackup import Layer

__author__ = 'davidc'
import unittest
from unittest.mock import Mock


class test_stackup_layers(unittest.TestCase):

    def setUp(self):
        self.p = Project.create()

    def test_basic(self):
        layer = Layer("foo", (1, 1, 1))
        self.p.stackup.add_layer(layer)

        self.assertIn(layer, self.p.stackup.layers)

        self.p.stackup.remove_layer(layer)

        self.assertNotIn(layer, self.p.stackup.layers)

    def test_callback_called_on_add_del(self):
        layer = Layer("foo", (1, 1, 1))

        call_me = Mock()

        self.p.stackup.changed.connect(call_me)
        self.p.stackup.add_layer(layer)

        self.assertTrue(call_me.called)
        ((model_change,), _) = call_me.call_args
        self.assertEqual(model_change.container, self.p.stackup.layers)
        self.assertEqual(model_change.what, layer)
        self.assertEqual(model_change.reason, ChangeType.ADD)

        call_me.reset_mock()
        self.p.stackup.remove_layer(layer)

        self.assertTrue(call_me.called)
        ((model_change,), _) = call_me.call_args
        self.assertEqual(model_change.container, self.p.stackup.layers)
        self.assertEqual(model_change.what, layer)
        self.assertEqual(model_change.reason, ChangeType.REMOVE)
