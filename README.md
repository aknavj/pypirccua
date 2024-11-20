# pypirccua

pypirccua - Python Pickering Relay Cycle Counting Utility Application is a PyQt-based application for visualizing and analyzing relay counts from DB files from Pickering PXI cards.

The **file format specification** is described in the [official reference manual](https://downloads.pickeringtest.info/downloads/RelayCountingApplication/RelayCountingAppHelp.pdf)

## License
- Under GNU/GPLv3

## Features
- Parses **RelayCount Card Database Files** (similar to the NI PXIe Health Monitor).
- Displays statistics on Pickering PXI card physical or logical layers.
- Allows users to set a **count heatmap** and provides **visual feedback** as a reference.
- Associates a `.db` file with a **table view**.

## Changelog

### [1.x.x] Future (somwhere in the future)

+ Support: **Interconnect DB data mapping** with the eBirst Card Definition set XML data, and visualize side-by-side with the default database **PiTableView**.
+ Support: **dataset export functionality** to Google Sheets.
+ Support: **PiLpxi & LXI client bridge functionality** into the application.
+ Support: additional statistics with an improved graph view (including support for zoom-in/out, selection, and callbacks in the table view).

### [1.1.0] - 2024-11-20

+ Added: Thread support for Db card loading.
+ Added: PiDbCardList support for removing and clearing card list.
+ Added: PiDbCardList detect already existing duplicates when adding Card DB File to the list.
+ Added: PircViewer proper ProgressBar, StatusBar for app feedbacking information to the user.
+ Added: PircViewer About dialog.
+ Added: PiTableView export table to csv functionality.

### [1.0.0] - 2024-11-17

+ Initial released version of the application.

## Screenshots

![initial db view](./assets/app1.png)

![dbfile -> table association](./assets/app2.png)

## Install using pypi
```
pip install pypirccua
```

### or upgrade package
```
pip install --upgrade pypirccua
```

### Run after pip installation
```
pypirccua
```

## Install from sources
```
pip install .
```

## Run from sources
```
python -m pypirccua
```
