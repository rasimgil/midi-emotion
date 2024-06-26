import torch
import re

# from torch._six import container_abcs, string_classes, int_classes
# from torch._six import string_classes
import collections

"""
Modified by Serkan Sulun
Filters out None samples
"""

""""Contains definitions of the methods used by the _DataLoaderIter workers to
collate samples fetched from dataset into Tensor(s).

These **needs** to be in global scope since Py2 doesn't support serializing
static methods.
"""

_use_shared_memory = False
r"""Whether to use shared memory in batch_collate"""

np_str_obj_array_pattern = re.compile(r"[SaUO]")

error_msg_fmt = "batch must contain tensors, numbers, dicts or lists; found {}"

numpy_type_map = {
    "float64": torch.DoubleTensor,
    "float32": torch.FloatTensor,
    "float16": torch.HalfTensor,
    "int64": torch.LongTensor,
    "int32": torch.IntTensor,
    "int16": torch.ShortTensor,
    "int8": torch.CharTensor,
    "uint8": torch.ByteTensor,
}


def filter_collate(batch):
    r"""Puts each data field into a tensor with outer dimension batch size"""

    if isinstance(batch, list) or isinstance(batch, tuple):
        batch = [i for i in batch if i is not None]  # filter out None s

    if batch != []:
        elem_type = type(batch[0])
        if isinstance(batch[0], torch.Tensor):
            out = None
            if _use_shared_memory:
                # If we're in a background process, concatenate directly into a
                # shared memory tensor to avoid an extra copy
                numel = sum([x.numel() for x in batch])
                storage = batch[0].storage()._new_shared(numel)
                out = batch[0].new(storage)
            return torch.stack(batch, 0, out=out)
        elif (
            elem_type.__module__ == "numpy"
            and elem_type.__name__ != "str_"
            and elem_type.__name__ != "string_"
        ):
            elem = batch[0]
            if elem_type.__name__ == "ndarray":
                # array of string classes and object
                if np_str_obj_array_pattern.search(elem.dtype.str) is not None:
                    raise TypeError(error_msg_fmt.format(elem.dtype))

                return filter_collate([torch.from_numpy(b) for b in batch])
            if elem.shape == ():  # scalars
                py_type = float if elem.dtype.name.startswith("float") else int
                return numpy_type_map[elem.dtype.name](list(map(py_type, batch)))
        elif isinstance(batch[0], float):
            return torch.tensor(batch, dtype=torch.float64)
        elif isinstance(batch[0], int):
            return torch.tensor(batch)
        elif isinstance(batch[0], str):
            return batch
        elif isinstance(batch[0], collections.abc.Mapping):
            return {key: filter_collate([d[key] for d in batch]) for key in batch[0]}
        elif isinstance(batch[0], tuple) and hasattr(batch[0], "_fields"):  # namedtuple
            return type(batch[0])(*(filter_collate(samples) for samples in zip(*batch)))
        elif isinstance(batch[0], collections.abc.Sequence):
            transposed = zip(*batch)
            return [filter_collate(samples) for samples in transposed]

        raise TypeError((error_msg_fmt.format(type(batch[0]))))
    else:
        return batch
