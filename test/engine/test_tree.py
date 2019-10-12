#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

from typing import *
from unittest import TestCase

from my_todo_app.engine.tree import TreeTraversal


class _MyTreeNode:

    def __init__(self):
        self.children: List[_MyTreeNode] = []


class _MyTreeTraversal(TreeTraversal):

    def __init__(self, nodes: List[_MyTreeNode]):
        super().__init__()
        self._nodes: List[_MyTreeNode] = nodes

    def children(self, self_: Any) -> List[Any]:
        self_node: _MyTreeNode = self_
        return self_node.children

    def parent(self, self_: Any) -> Optional[Any]:
        for node in self._nodes:
            if self_ in node.children:
                return node
        return None


class TestTreeTraversal(TestCase):

    def test_it_works(self):
        root = _MyTreeNode()
        root.children.append(_MyTreeNode())
        root.children.append(_MyTreeNode())
        root.children[0].children.append(_MyTreeNode())
        root.children[0].children.append(_MyTreeNode())
        root.children[1].children.append(_MyTreeNode())

        nodes: List[_MyTreeNode] = [root,
                                    root.children[0],
                                    root.children[0].children[0],
                                    root.children[0].children[1],
                                    root.children[1],
                                    root.children[1].children[0]]

        traversal = _MyTreeTraversal(nodes)

        self.assertSequenceEqual(root.children[0].children, traversal.children(root.children[0]))
        self.assertSequenceEqual(nodes[1:], traversal.descendants(root))
        self.assertSequenceEqual(nodes, traversal.descendants_and_self(root))
        self.assertEqual(root.children[1], traversal.parent(root.children[1].children[0]))
        self.assertSequenceEqual([root.children[1], root], traversal.ancestors(root.children[1].children[0]))
