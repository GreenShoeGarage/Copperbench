# Pan and zoom — v1.6.3

The **Pan** button beside **Fit** moves the view, not the PCB objects. It works
in **Bench**, **Copper**, and **Fabrication**, on either board face. There is no
new permanent instruction banner: use the active tool's **?** for details.

## Controls

| Control | Action |
| --- | --- |
| **Pan** button or **P** | Toggle navigation mode. Drag anywhere on the canvas, including over a component or trace. |
| **Space + drag** | Temporarily pan without abandoning a trace, selected leads, or pending component/block placement. |
| **Middle-button drag** | Temporarily pan in any tool. |
| **Wheel / two-finger trackpad scroll** with Pan on | Pan horizontally and vertically using the input's scroll deltas. |
| **Wheel** with Pan off | Retain the existing zoom-at-pointer behavior. |
| **Ctrl/Command + wheel** | Zoom at the pointer even while Pan is on. A trackpad pinch reported as Ctrl-wheel uses this path. |
| **Shift + wheel** | Pan horizontally. |
| **One finger** with Pan on | Drag the view without editing the object underneath. |
| **Two fingers on a touchscreen** | Pan and pinch around the gesture centre in any tool. |
| **Arrow keys** with Pan on and canvas focused | Translate the view by 40 screen pixels; hold Shift for 120 pixels. |
| **Fit** or **Home** | Recentre and fit the current board. |
| **P**, **Pan**, or **Escape** | Leave Pan and return to the existing tool. Escape first exits navigation; a subsequent Escape cancels the underlying operation. |

The cursor changes from an open hand to a closed hand during a pan. Pan remains
active after releasing the drag until it is toggled off or an editing tool is
chosen. Rotation, deletion and other editing shortcuts do not operate on a
hidden selection while Pan is active. Inspector controls remain explicit editing
commands. **V** exits Pan to Select; picking a drawing tool or a part also exits
Pan. Keyboard shortcuts do not intercept text inputs, dialogs, or browser print.

## What stays unchanged

Panning changes only the in-memory camera offset. It does not translate or resize
parts, pads, traces, vias, holes, silkscreen, keepouts, or the board outline. It
does not add an undo entry, dirty the save indicator, or change generated Gerber
and drill bytes. The selection and unfinished operation survive temporary panning.
The camera position is not serialized into project JSON. Native schema remains 5.

Pointer capture keeps a drag going when it crosses the canvas boundary. Losing
focus, pointer capture, or a cancelled gesture releases the drag. If a second
finger joins an uncommitted component drag, the tentative edit is rolled back
before the two-finger camera gesture begins. A single touch that will place an
object or advance a drawing is deferred until release, so the first finger of a
two-finger gesture cannot accidentally create a part, via, hole, or waypoint.
After a pinch, lift all fingers before starting a new edit.

## Input and test boundaries

No input-device heuristics, network calls, or new dependencies were added. Wheel
units are normalized for pixel, line, and page deltas. The implementation follows
[Pointer Events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)
and the documented [wheel delta units](https://developer.mozilla.org/en-US/docs/Web/API/WheelEvent/deltaMode).
Actual hardware/browser gesture mapping can vary; **Pan + drag**, **Space + drag**,
and **Fit** remain direct controls rather than depending on trackpad detection.

Automated touch tests inject trusted input through Chromium's DevTools protocol;
they are not physical phone/trackpad tests. See [the verification record](TESTING.md).
