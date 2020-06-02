# XindeX

XindeX is an easy to learn and use GUI application for creating, editing,
and outputting indexes (e.g., for books).

First install Python (>= 3.6), and then the Python packages, PySide (i.e.,
PySide1 for Qt 4.8), APSW, and roman. Then install txt2tags.

Then download and unzip (or clone) XindeX.

Then cd into the XindeX folder and run:
`txt2tags -t html t2t/*.t2t`
(This will generate the online help accessible by clicking Help→Help or
pressing F1 from inside XindeX.)

Then run:
`rcc.sh`
(This will create the Qt resource file that contains the application's
images.)

Then run (or double-click) `XindeX.pyw`.

It should run fine on Windows but nowadays we only test on Linux.

![Screenshot](screenshot.png)

## License

GPL-3.0.
