---
layout: post
title:  "Querying Raster Layers with Raster Attribute Tables"
date:   2026-01-21 10:00:00 +1000
categories: tutorial
---

# Introduction

In a [previous post](../16/tuiview-query.html) we looked at querying
continuous rasters with TuiView. In this post we look at querying
thematic rasters in TuiView. TuiView treats any raster with an 
attribute table as thematic.

Outputs from [pyshepseg](https://www.pyshepseg.org/en/latest/) 
generally contain raster attribute tables. See our 
[previous post](../../2025/12/11/pyshepseg-intro.html) on 
performing a segmentation and gathering statistics that are
put into the rater attribute table.

KEA and HFA are the only GDAL drivers that currently properly support
raster attribute tables (RAT) natively. For some drivers (like GeoTiff)
GDAL saves the RATs in a sidecar .xml file. This can be very inefficient
and slow for large RATs so we recommend using KEA or HFA where possible.
Some drivers (again, like GeoTiff) support a similar idea, but just for colours: 
Colour Tables. 

Raster attribute tables can have colour columns. If the RAT has 
colour tables, or there is a Colour Table present, you can ask that TuiView 
open the file as "Color Table" and you will see the behaviour described in this 
post. This is the default behaviour of TuiView
but can be overriden in the the stretch dialog, or in the default stretch.

# Querying Thematic Rasters

If you open a file that has a Raster Attribute Table with colours, you will
see something like the following when you press the Query Button (![Query Window](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/query.png)):

![Query Window]({{site.url}}/images/tuiview_ratquery.png)

Note that the image is displayed using the colours in the colour table. Also,
note how that the color columns in the RAT have been converted to a single
"Color" column with the actual colour shown as a rectangle. The other
columns of the RAT are shown with their values. The rows are also numbered
on the left and the table can be scrolled up and down.

# Highlighting a row in the table and highlighting areas of the raster by selecting rows

If you click on the raster with the Query Tool, the corresponding row will 
be highlighted in yellow and the table and the table will be scrolled to 
show that row. 
If you click on a row it is selected. TuiView makes a distinction between
highlighted and selected rows. Selected rows are shown in blue in the
table. You can select more than one row by holding down the Ctrl key before
clicking another row - the first one will stay selected. You can add as
many rows as you like to the selection using this method. If you want to select
a range of rows, click the first row of the range then while holding the Shift
key, click the last row. The rows you clicked on will be selected along
with the rows between.
By default, the areas on the map that correspond to the selected row(s) will
be highlighted in yellow. You can prevent the map being highlighted using the
Highlight Selection button ![Highlight Selection](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/highlight.png) 
on the toolbar. Next to this button is a yellow button that allows you to change
the selection colour. Clicking this brings up a colour chooser and when 
you select a colour, selected rows are shown as this colour on the map and the 
colour of this button on the toolbar is updated.
There are also buttons to remove all selected rows (![Remove Selection](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/removeselection.png))
and select all rows (![Select All](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/selectall.png)).

This "Faster Forward" and "Rewind" Buttons can be used to scroll up or down to the
next selected row(s) in the table.

# Geographical Selection

You can also select rows by selecting areas on the map. There are
3 ways to do this: by polygon, by line and by point.
To select rows by polygon, select the Geographic Selection by Polygon Tool
(![Polygon](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/geographicselect.png)).
Then on the map, left click the first vertex of the polygon, then the next and the next.
When you have finished, right click and the polygon will be closed. The rows
that intersect with this polygon will be highlighted on the map and selected
in the table:

![Geographic Select]({{site.url}}/images/tuiview_geogselect.png)

You can also select rows that sit along a long using the Geographic Select
by Line Tool (![Line](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/geographiclineselect.png)).
This operates similiarly to the Profile Tool. Left click on the start of the line, and
any vertices. Right click to end the line. Rows that intersect the line will
be highlighted on the map and selected in the table.

Lastly, you can select points using the Geographic Select by Point Tool
(![Point](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/geographicpointselect.png)).
Simply click a point on the map and the row for that point will be highlighted.


