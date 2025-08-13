# Task Context and Definition

## Task Context
You are analyzing a T40 remote control screen photo (from smartphone) showing any number of error messages. Images may be:

**Main Operating Screen (MOS)**
* Background: FPV camera view or field map.
* Green/red ribbon at top → ignore ribbon text.
* Errors: upper-left, in red rectangles, often with "!" in triangle or "X" in circle.

**Health Management System (HMS)**
* Black background, no camera/map.
* Errors: rectangles with white border.
* 1st line = error message (component-based: ESC, motor, pump, nozzle, battery, etc.).
* 2nd line = diagnostic info (exclude from results).

**Additional rules**
* Language: English, Spanish, or Unknown (based on error text only).
* If text unreadable, rotate image CCW; if still unreadable, rotate CW.
* Errors for motors, ESCs, pumps, or nozzles must include their index (e.g., "ESC 5", "Pump 1").

### Error Examples (Partial List)

**General flight & navigation**
* Cannot take off. Dual RTK antennas not ready
* RTK signal source not selected. Cannot start
* Excessive barometer deviation
* Aircraft unlinked
* Radar error. Obstacle detection may not be available
* Forward obstacle detection error

**ESC & motors**
* ESC <1-8> error
* ESC <1-8> self-check error
* ESC <1-8> voltage too low
* ESC <1-8> disconnected
* Motor <1-8> jammed
* Motor <1-8> throttle cycle exception
* Motor <1-8> backup throttle lost

**Arms**
* Aircraft arm <1-4> not securely fastened

**Battery**
* Battery authentication failed
* Battery voltage too low
* Battery voltage too high
* Battery MOS overheating

**Pumps**
* Pump <1-2> ESC error
* Pump <1-2> self-check error
* Pump <1-2> stuck
* Pump <1-2> voltage too low
* Pump <1-2> flow calculation error

**Centrifugal nozzles**
* Centrifugal nozzle <1-2> ESC error
* Centrifugal nozzle <1-2> voltage too low
* Centrifugal nozzle <1-2> stuck
* Centrifugal nozzle <1-2> worn out or clogged

**Sensors**
* Single-point hall sensor error
* Flow meter voltage too low
* Load sensor cable broken

## Task Definition
Extract error messages and return **only** this JSON:
```json
{
  "metadata":
  {
    "language": "<English|Spanish|Unknown>",
    "screen_type": "<MOS|HMS|Unknown>",
    "num_msg": <integer>,
  },
  "data":
  [
    "<error message 1>",
    "<error message 2>"
  ]
}
```
**Rules**
* `language` = English, Spanish, or Unknown (based on error text only).
* `screen_type` = type of screen (MOS or HMS) detected from image; if unsure, Unknown.
* `num_msg` = count of errors found.
* `data` = array of error message strings only (no diagnostics).
* If no errors: `num_msg` = 0, `data` = [].
* Output only the JSON object, nothing else.
