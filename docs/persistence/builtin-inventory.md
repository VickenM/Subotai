# Built-in parameter and port inventory

Source baseline: `9e77b2f` (2026-10-02). All 44 registered built-in type declarations are listed below.
This is documentation, not a runtime inventory or loader input. Node-owned declarations will be authoritative in #29; this reference should then be generated from those declarations.
Extracted from constructor syntax without importing or executing nodes. Defaults below are Python source expressions,
not proposed JSON encodings. `PARAM=4`, `INPUT_PLUG=1`, `OUTPUT_PLUG=2`, `NONE=0`.
Inherited promotion fields are included. Dynamic `stringN` inputs are described in the contract.
Read with the [state policies](contract.md#node-specific-state-policies); output flags alone do not decide persistence.

## APIListener

Source: [eventnodes/apilistener.py](../../eventnodes/apilistener.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'connected'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'received'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'session'` | `QueueParam` | `OUTPUT_PLUG` | `self.queue` |
| `'response'` | `StringParam` | `OUTPUT_PLUG` | `''` |

## APIRequest

Source: [eventnodes/apirequest.py](../../eventnodes/apirequest.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'session'` | `QueueParam` | `INPUT_PLUG` | `None` |
| `'request'` | `StringParam` | `INPUT_PLUG &#124; PARAM` | `'n'` |

## BlendImage

Source: [eventnodes/image/blend.py](../../eventnodes/image/blend.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image1'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image2'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'blend_mode'` | `BlendOpParam` | `PARAM` | `BlendOpParam.Operations.overlay` |

## BooleanParameter

Source: [eventnodes/parameter.py](../../eventnodes/parameter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'promote state'` | `BoolParam` | `NONE` | `False` |
| `'promote name'` | `StringParam` | `NONE` | `None` |
| `'param'` | `BoolParam` | `OUTPUT_PLUG &#124; PARAM` | `True` |

## Brightness/Contrast

Source: [eventnodes/image/brightnesscontrast.py](../../eventnodes/image/brightnesscontrast.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'brightness'` | `FloatParam` | `PARAM` | `1.0` |
| `'contrast'` | `FloatParam` | `PARAM` | `1.0` |

## Collector

Source: [eventnodes/collector.py](../../eventnodes/collector.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'emit'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'item'` | `StringParam` | `INPUT_PLUG` | `''` |
| `'items'` | `ListParam` | `OUTPUT_PLUG` | `[]` |

## Color

Source: [eventnodes/image/color.py](../../eventnodes/image/color.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'color'` | `FloatParam` | `PARAM` | `1.0` |

## Condition

Source: [eventnodes/condition.py](../../eventnodes/condition.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'true'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'false'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'operation'` | `CompareParam` | `PARAM` | `CompareParam.Operations.equal` |
| `'value1'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |
| `'value2'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |

## ConsoleWriter

Source: [eventnodes/consolewriter.py](../../eventnodes/consolewriter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'prefix'` | `StringParam` | `PARAM` | `'%m/%d/%Y, %H:%M:%S'` |
| `'message'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |

## CopyFile

Source: [eventnodes/copyfile.py](../../eventnodes/copyfile.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'source'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'d:\\temp\\source.txt'` |
| `'destination'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'d:\\temp\\target.txt'` |
| `'destination'` | `StringParam` | `OUTPUT_PLUG` | `'d:\\temp\\target.txt'` |

## Counter

Source: [eventnodes/counter.py](../../eventnodes/counter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'reset'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'initial'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'increment'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `1` |
| `'value'` | `IntParam` | `OUTPUT_PLUG` | `0` |

## CropImage

Source: [eventnodes/image/crop.py](../../eventnodes/image/crop.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `PARAM &#124; INPUT_PLUG` | `None` |
| `'left'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'upper'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'right'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'lower'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'image'` | `ImageParam` | `PARAM &#124; OUTPUT_PLUG` | `''` |

## CurrentDir

Source: [eventnodes/currentdir.py](../../eventnodes/currentdir.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'directory'` | `StringParam` | `OUTPUT_PLUG` | `''` |

## DirChanged

Source: [eventnodes/dirchange.py](../../eventnodes/dirchange.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'directory'` | `StringParam` | `OUTPUT_PLUG &#124; PARAM` | `''` |
| `'new'` | `ListParam` | `OUTPUT_PLUG` | `[]` |
| `'removed'` | `ListParam` | `OUTPUT_PLUG` | `[]` |

## Download

Source: [eventnodes/download.py](../../eventnodes/download.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'url'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'filename'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'filename'` | `StringParam` | `OUTPUT_PLUG` | `''` |

## Email

Source: [eventnodes/email.py](../../eventnodes/email.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'sender'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'my.name@gmail.com'` |
| `'recipients'` | `ListParam` | `PARAM &#124; INPUT_PLUG` | `[StringParam(name='', value='my.name@gmail.com')]` |
| `'subject'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'message'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'attachments'` | `ListParam` | `PARAM &#124; INPUT_PLUG` | `[]` |
| `'server'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'smtp.gmail.com'` |
| `'port'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `587` |
| `'username'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'my.name@gmail.com'` |
| `'password'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'use_tls'` | `BoolParam` | `PARAM &#124; INPUT_PLUG` | `True` |

## FilesChanged

Source: [eventnodes/fileschanged.py](../../eventnodes/fileschanged.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'files'` | `ListParam` | `PARAM` | `[StringParam(name='', value='')]` |

## FloatParameter

Source: [eventnodes/parameter.py](../../eventnodes/parameter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'promote state'` | `BoolParam` | `NONE` | `False` |
| `'promote name'` | `StringParam` | `NONE` | `None` |
| `'param'` | `FloatParam` | `OUTPUT_PLUG &#124; PARAM` | `0.0` |

## For

Source: [eventnodes/for_.py](../../eventnodes/for_.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'finished'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'start'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |
| `'end'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |
| `'step'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `1` |
| `'current'` | `IntParam` | `OUTPUT_PLUG` | `0` |

## ForEach

Source: [eventnodes/foreach.py](../../eventnodes/foreach.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'finished'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'items'` | `ListParam` | `PARAM &#124; INPUT_PLUG` | `[]` |
| `'item'` | `StringParam` | `OUTPUT_PLUG` | `''` |
| `'index'` | `IntParam` | `OUTPUT_PLUG` | `0` |
| `'count'` | `IntParam` | `OUTPUT_PLUG` | `0` |

## FormatString

Source: [eventnodes/formatstring.py](../../eventnodes/formatstring.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'format'` | `StringParam` | `PARAM` | `''` |
| `'string1'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'string'` | `JoinParam` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## Hotkey

Source: [eventnodes/hotkey.py](../../eventnodes/hotkey.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'hotkey'` | `StringParam` | `PARAM` | `''` |

## IntToStr

Source: [eventnodes/inttostr.py](../../eventnodes/inttostr.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'integer'` | `IntParam` | `INPUT_PLUG` | `0` |
| `'zeropad'` | `IntParam` | `PARAM` | `0` |
| `'string'` | `ToStr` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## IntegerParameter

Source: [eventnodes/parameter.py](../../eventnodes/parameter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'promote state'` | `BoolParam` | `NONE` | `False` |
| `'promote name'` | `StringParam` | `NONE` | `None` |
| `'param'` | `IntParam` | `OUTPUT_PLUG &#124; PARAM` | `0` |

## JoinStrings

Source: [eventnodes/joinstrings.py](../../eventnodes/joinstrings.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'first'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'second'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'separator'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'string'` | `JoinParam` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## JoinStringsMulti

Source: [eventnodes/joinstringsmulti.py](../../eventnodes/joinstringsmulti.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'string1'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'separator'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'string'` | `JoinParam` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## ListDir

Source: [eventnodes/listdir.py](../../eventnodes/listdir.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'directory'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'pattern'` | `StringParam` | `PARAM` | `'*.*'` |
| `'recursive'` | `BoolParam` | `PARAM` | `False` |
| `'fullpaths'` | `BoolParam` | `PARAM` | `False` |
| `'files'` | `ListParam` | `OUTPUT_PLUG` | `[]` |

## Math

Source: [eventnodes/math.py](../../eventnodes/math.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'operation'` | `MathOpParam` | `PARAM` | `MathOpParam.Operations.add` |
| `'value1'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |
| `'value2'` | `IntParam` | `INPUT_PLUG &#124; PARAM` | `0` |
| `'result'` | `MathParam` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## MultiProcess

Source: [eventnodes/multiprocess.py](../../eventnodes/multiprocess.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'concurrency'` | `IntParam` | `PARAM` | `0` |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'process'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'arguments'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |

## OpenImage

Source: [eventnodes/image/open.py](../../eventnodes/image/open.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'file'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'width'` | `IntParam` | `OUTPUT_PLUG` | `0` |
| `'height'` | `IntParam` | `OUTPUT_PLUG` | `0` |

## Process

Source: [eventnodes/process.py](../../eventnodes/process.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'process'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'arguments'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |

## ResizeImage

Source: [eventnodes/image/resize.py](../../eventnodes/image/resize.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `PARAM &#124; INPUT_PLUG` | `None` |
| `'width'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'height'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'image'` | `ImageParam` | `PARAM &#124; OUTPUT_PLUG` | `None` |

## Rotate

Source: [eventnodes/image/rotate.py](../../eventnodes/image/rotate.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'amount'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |

## SaveImage

Source: [eventnodes/image/save.py](../../eventnodes/image/save.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `PARAM &#124; INPUT_PLUG` | `None` |
| `'filename'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |

## SliceList

Source: [eventnodes/slicelist.py](../../eventnodes/slicelist.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'start'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'end'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `-1` |
| `'list'` | `ListParam` | `INPUT_PLUG` | `[]` |
| `'list'` | `SliceParam` | `OUTPUT_PLUG` | `(inherited default / computed)` |

## SplitString

Source: [eventnodes/splitstring.py](../../eventnodes/splitstring.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'source'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'pattern'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `'\\'` |
| `'parts'` | `ListParam` | `OUTPUT_PLUG` | `[]` |

## StringParameter

Source: [eventnodes/parameter.py](../../eventnodes/parameter.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'promote state'` | `BoolParam` | `NONE` | `False` |
| `'promote name'` | `StringParam` | `NONE` | `None` |
| `'param'` | `StringParam` | `OUTPUT_PLUG &#124; PARAM` | `''` |

## SystemNotification

Source: [eventnodes/systemnotification.py](../../eventnodes/systemnotification.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'title'` | `StringParam` | `PARAM` | `''` |
| `'message'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'icon'` | `ImageParam` | `INPUT_PLUG` | `None` |

## ThumbnailImage

Source: [eventnodes/image/thumbnail.py](../../eventnodes/image/thumbnail.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `PARAM &#124; INPUT_PLUG` | `None` |
| `'width'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'height'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'image'` | `ImageParam` | `PARAM &#124; OUTPUT_PLUG` | `None` |

## Timer

Source: [eventnodes/timer.py](../../eventnodes/timer.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'interval'` | `IntParam` | `PARAM` | `1000` |

## Translate

Source: [eventnodes/image/translate.py](../../eventnodes/image/translate.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `INPUT_PLUG` | `None` |
| `'image'` | `ImageParam` | `OUTPUT_PLUG` | `None` |
| `'x_offset'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |
| `'y_offset'` | `IntParam` | `PARAM &#124; INPUT_PLUG` | `0` |

## UnzipFile

Source: [eventnodes/unzipfile.py](../../eventnodes/unzipfile.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'zipfile'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'target'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'target'` | `StringParam` | `OUTPUT_PLUG` | `''` |

## Viewer

Source: [eventnodes/viewer.py](../../eventnodes/viewer.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'image'` | `ImageParam` | `INPUT_PLUG` | `None` |

## ZipFile

Source: [eventnodes/zipfile.py](../../eventnodes/zipfile.py)

| Binding | Class | Flags | Constructor default |
| --- | --- | --- | --- |
| `'event'` | `Signal` | `INPUT_PLUG` | `(inherited default / computed)` |
| `'event'` | `Signal` | `OUTPUT_PLUG` | `(inherited default / computed)` |
| `'source'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'zipfile'` | `StringParam` | `PARAM &#124; INPUT_PLUG` | `''` |
| `'zipfile'` | `StringParam` | `OUTPUT_PLUG` | `''` |
