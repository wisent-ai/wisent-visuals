# Charts

`wisent-chart --spec <file|-> --output <path.svg|path.png>` draws one Wisent
brand chart. The spec is JSON; `kind` names the family and every other field is
that family's. A field the family does not take is refused, and so is a missing
required one, naming the field.

The chart's size is always given: `width` and `height` in pixels. A `title`
left out takes the family's design title.

## Families

| `kind` | Required fields | Optional fields | Styles |
|---|---|---|---|
| `area` | `style`, `width`, `height`, `x`, `y_series` (exactly three, stacked bottom to top) | `labels`, `title` | 1 edge, 2 gradient, 3 pattern, 4 two patterns, 5 solid colours; or `solid`, `gradient`, `pattern`, `2patterns`, `minimal` |
| `bar` | `style`, `theme`, `width`, `height`, `categories`, `series`, `labels` | `title` | 1 solid, 2–4 patterned middle segment, 5 multicolour; or `solid`, `pattern1`, `pattern2`, `pattern3`, `multicolor` |
| `column` | as `bar` | `title` | as `bar` |
| `line` | `style`, `width`, `height`, `line_width`, `x`, `y_series` | `labels`, `colors`, `title` | 1–3 dark (solid, markers, shapes), 4–6 the same on white; or `solid`, `markers`, `shapes` |
| `pie` | `style`, `width`, `height`, `values`, `labels` | `title`, `center_label`, `center_value` | 1 brand, 2 black, 3 white |
| `radar` | `style`, `width`, `height`, `data_series`, `labels` | `axis_labels`, `title` | 1 brand, 2 black, 3 white |
| `bubble` | `style`, `width`, `height`, `chart`, `sizes` | `categories`, `category_labels`, `title` | 1 brand, 2 black, 3 white; or `brand`, `black`, `white` |

`theme` is `brand`, `black` or `white`. A bubble `chart` is
`{"type": "bubble", "x_data": [...], "y_data": [...]}` or
`{"type": "radar", "angles": [...], "distances": [...]}` with angles in degrees
clockwise from twelve o'clock and distances on 0–100. Radar values are on
0–100 too; a radar chart has one axis per value of its first series.

Axis labels come from the data: line and area charts label each x value as
written, bubble charts label their axes with the range of the data, and a pie
chart's `center_value` defaults to the whole-number sum of `values`.

## Refusals

| Message | Meaning |
|---|---|
| `<spec> is not a chart spec: unknown field …` / `missing field …` | The spec does not match its family's fields. |
| `Unknown style name: …. Valid names are: …` | A style name the family does not have. |
| `… style must be …, got N` / `Style must be between 1 and 5, got N` | A style number outside the family's styles. |
| `series N has M values but there are K categories` / `… x values` | The series do not line up with the categories or x values. |
| `the area designs stack 3 series, got N` | Area charts draw exactly three bands. |
| `the largest … is N, so no … has a … to scale` | Every value is zero or negative, so nothing has a size. |
| `<path>: output must use .svg or .png` | The output suffix names no format the command writes. |

## Example

```bash
wisent-chart --spec - --output radar.svg <<'JSON'
{"kind": "radar", "style": 2, "width": 328, "height": 328,
 "data_series": [[80, 60, 70, 90, 50, 65, 75, 85]], "labels": ["One"]}
JSON
```
