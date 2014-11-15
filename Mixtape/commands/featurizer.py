from __future__ import print_function, absolute_import
import os
import sys
import glob

from ..cmdline import NumpydocClassCommand, argument
from ..utils import verbosedump
import numpy as np
import mdtraj as md
from ..featurizer import (AtomPairsFeaturizer, SuperposeFeaturizer,
                          DRIDFeaturizer, DihedralFeaturizer,
                          ContactFeaturizer)


class FeaturizerCommand(NumpydocClassCommand):
    trjs = argument(
        '--trjs', help='Glob pattern for trajectories',
        default='', nargs='+')
    top = argument(
        '--top', help='Path to topology file', default='')
    chunk = argument(
        '--chunk',
        help='''Chunk size for loading trajectories using mdtraj.iterload''',
        default=10000, type=int)
    out = argument(
        '--out', required=True, help='Output path')
    stride = argument(
        '--stride', default=1, type=int,
        help='Load only every stride-th frame')


    def start(self):
        print(self.instance)
        if os.path.exists(self.top):
            top = md.load(self.top)
        else:
            top = None

        dataset = []
        for item in self.trjs:
            for trjfn in glob.glob(item):
                trajectory = []
                iterloader = md.iterload(trjfn, stride=self.stride,
                                         chunk=self.chunk, top=top)
                for i, chunk in enumerate(iterloader):
                    fstr = '\r{} chunk {}'
                    fval = (os.path.basename(trjfn), i)
                    print(fstr.format(*fval), end='')
                    sys.stdout.flush()
                    trajectory.append(self.instance.partial_transform(chunk))
                print()
                dataset.append(np.concatenate(trajectory))

        verbosedump(dataset, self.out)
        print('All done')


class DihedralFeaturizerCommand(FeaturizerCommand):
    _concrete = True
    klass = DihedralFeaturizer


class AtomPairsFeaturizerCommand(FeaturizerCommand):
    klass = AtomPairsFeaturizer
    _concrete = True

    def _pair_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=2)


class SuperposeFeaturizerCommand(FeaturizerCommand):
    klass = SuperposeFeaturizer
    _concrete = True

    def _reference_traj_type(self, fn):
        return md.load(fn)

    def _atom_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=1)


class DRIDFeaturizerCommand(FeaturizerCommand):
    klass = DRIDFeaturizer
    _concrete = True

    def _atom_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=1)


class ContactFeaturizerCommand(FeaturizerCommand):
    _concrete = True
    klass = ContactFeaturizer

    def _contacts_type(self, val):
        if val is 'all':
            return val
        else:
            return np.loadtxt(val, dtype=int, ndmin=2)