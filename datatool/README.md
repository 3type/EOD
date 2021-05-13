# DataTool for EOD

This is the datatool package for Glyphs Plug-in 'Explosive Ordnance Disposal' aka EOD or 拆字小组.

## datatool-idsDict.py

Package the IDS data into python pickle object, then save to .pdata file with gzip.

### What's IDS data?
**Ideographic Description Sequence**, based on ISO/IEC 10646-1:2000 F.3.1; however Compatibility Ideographs and non-UCS Ideographs are also allowed.

We use the [chise IDS data project](https://gitlab.chise.org/CHISE/ids)(also on [github](https://github.com/chise/ids)) as the data source of the EOD project.

You can hack the code to make your own database.

## datatool-uniSet.py

Package the character set into python pickle object, then save to .pdata file with gzip.

### Character set

Since EOD was originally a plug-in designed for Chinese characters, we selected three character sets commonly used in the font industry.

- GB 2312
- GBK (Big5)
- HanYi-9196 (汉仪常用字表)

You can hack the code to add your own sets.

## License

Copyright 2020-2021 3type 三言.

* License

This package is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

This package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this package; see the file COPYING.  If not, write to
the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.