# pypirccua

This humble project introduces a **Relay Cycle Counting utility application** implemented in Python. The utility functions as a **pxi database file parser** and data viewer, with some **basic statistics** (questionable).

The **file format specification** is described in the [official reference manual](https://downloads.pickeringtest.info/downloads/RelayCountingApplication/RelayCountingAppHelp.pdf)

## License
- Under GNU/GPL

## Features
- Parses **RelayCount Card Database Files** (similar to the NI PXIe Health Monitor).
- Displays statistics on Pickering PXI card physical or logical layers.
- Allows users to set a **count heatmap** and provides **visual feedback** as a reference.
- Associates a `.db` file with a **table view**.

## Future Nice-to-Haves
1. **Interconnect DB data mapping** with the eBirst Card Definition set XML data, and visualize side-by-side with the default database **CardTableView**.
2. If time permits: 
   - Implement **PiLpxi & LXI client bridge functionality** into the application.
   - Add **dataset export functionality** to Google Sheets.
   - Introduce additional statistics with an improved graph view (including support for zoom-in/out, selection, and callbacks in the table view).

## Screenshots

![initial db view](./imgs/app1.png)

![dbfile -> table association](./imgs/app2.png)

## Dependencies

**matplotlib**
```
pip install matplotlib
```

**PyQT5**
```
pip install PyQt5
```

## Run
```
python pircviewer.py
```
