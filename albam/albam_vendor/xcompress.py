import os
import ctypes

# wrapper for xcompress64.dll library based on https://github.com/emoose/re4-research/blob/master/re4lfs.cpp
# ctypes bindings for xcompress64.dll
dll_path = os.path.join(os.path.dirname(__file__), "xcompress64.dll")
print("path to xcompress: ", dll_path)
xcompress = ctypes.WinDLL(dll_path)

XMemCreateDecompressionContext = xcompress.XMemCreateDecompressionContext
XMemCreateDecompressionContext.restype = ctypes.c_uint32
# int algo, void* params, uint32_t param_size, void** context
XMemCreateDecompressionContext.argtypes = [ctypes.c_int,
                                           ctypes.c_void_p,
                                           ctypes.c_uint32,
                                           ctypes.POINTER(ctypes.c_void_p)]

XMemDestroyDecompressionContext = xcompress.XMemDestroyDecompressionContext
XMemDestroyDecompressionContext.restype = None
XMemDestroyDecompressionContext.argtypes = [ctypes.c_void_p]

XMemDecompress = xcompress.XMemDecompress
XMemDecompress.restype = ctypes.c_uint32
# void* context, void* destination buffer, size_t* dest size, void* source buffer, size_t source size
XMemDecompress.argtypes = [ctypes.c_void_p,
                           ctypes.c_void_p,
                           ctypes.POINTER(ctypes.c_size_t),
                           ctypes.c_void_p,
                           ctypes.c_size_t]

XMemCreateCompressionContext = getattr(xcompress, "XMemCreateCompressionContext", None)
XMemCompress = getattr(xcompress, "XMemCompress", None)
XMemDestroyCompressionContext = getattr(xcompress, "XMemDestroyCompressionContext", None)
if XMemCreateCompressionContext:
    XMemCreateCompressionContext.restype = ctypes.c_uint32
    XMemCreateCompressionContext.argtypes = [ctypes.c_int,
                                             ctypes.c_void_p,
                                             ctypes.c_uint32,
                                             ctypes.POINTER(ctypes.c_void_p)]
if XMemCompress:
    XMemCompress.restype = ctypes.c_uint32
    XMemCompress.argtypes = [ctypes.c_void_p,
                             ctypes.c_void_p,
                             ctypes.POINTER(ctypes.c_size_t),
                             ctypes.c_void_p,
                             ctypes.c_size_t]
if XMemDestroyCompressionContext:
    XMemDestroyCompressionContext.restype = None
    XMemDestroyCompressionContext.argtypes = [ctypes.c_void_p]


def xcompress_decompress(compressed_data, decompressed_size):
    context = ctypes.c_void_p()
    result = XMemCreateDecompressionContext(1, None, 0, ctypes.byref(context))
    if result != 0:
        raise RuntimeError(f"Failed to create decompression context. Error code: {result}")

    try:
        dest_size = ctypes.c_size_t(decompressed_size)
        dest_buffer = (ctypes.c_ubyte * decompressed_size)()
        src_size = len(compressed_data)
        src_buffer = (ctypes.c_ubyte * src_size).from_buffer_copy(compressed_data)

        result = XMemDecompress(context, dest_buffer, ctypes.byref(dest_size), src_buffer, src_size)
        if result != 0:
            raise RuntimeError(f"Decompression failed. Error code: {result}")

        return bytes(dest_buffer)[:dest_size.value]
    finally:
        XMemDestroyDecompressionContext(context)
