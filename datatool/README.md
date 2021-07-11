# DataTool for EOD

This is the datatool package for Glyphs Plug-in 'Explosive Ordnance Disposal' aka EOD or 拆字小组.

## What's IDS data?

**I**deographic **D**escription **S**equence is a way to describe the structure of CJK Unified ideographs, described in chapter 18.2 of the [Unicode Standard](https://www.unicode.org/versions/latest/ch18.pdf); however, compatibility ideographs and non-UCS ideographs are also allowed.

We use the [chise IDS data project](https://gitlab.chise.org/CHISE/ids) (also on [GitHub](https://github.com/chise/ids)) as the data source of the EOD project.

You can hack the following code to make your own database:

- `datatool-idsDict.py`: package the IDS data into python pickle object, then save to `.pdata` file with gzip.

### Character set

Since EOD was originally a plug-in designed for Chinese characters, we selected three character sets commonly used in the font industry.

- GB 2312
- GBK (Big5)
- HanYi-9196 (汉仪常用字表)

You can hack the following code to add your own sets:

- `datatool-uniSet.py`: package the character set into python pickle object, then save to `.pdata` file with gzip.

## License

Copyright © 2020–2021 3type

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
