#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import copy
import zipfile

from Const import UTF8


DOCUMENT = "word/document.xml"
STYLES = "word/styles.xml"


def output(config, document):
    parts = copy.deepcopy(Parts) # Preserve original
    parts[DOCUMENT] = document.replace("<w:r><w:t></w:t></w:r>", "")
    parts[STYLES] = parts[STYLES].format(family=config.StdFont,
                                         size=config.StdFontSize * 2)
    with zipfile.ZipFile(config.Filename, "w",
                         zipfile.ZIP_DEFLATED) as file:
        for filename, content in parts.items():
            if filename != DOCUMENT:
                content = content.replace("\n", "")
            file.writestr(filename, content.encode(UTF8))


Parts = collections.OrderedDict()
Parts["[Content_Types].xml"] = """
<?xml version="1.0"?>
<Types xmlns="http://schemas.openxmlformats.
org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.
openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/vnd.
openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.
openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.
openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""
Parts["word/numbering.xml"] = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.
org/wordprocessingml/2006/main" />
"""
Parts["word/styles.xml"] = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.\
org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/>
<w:qFormat/>
<w:rPr>
    <w:rFonts w:ascii="{family}" w:hAnsi="{family}"/>
    <w:sz w:val="{size}"/>
</w:rPr>
</w:style>
</w:styles>
"""
Parts["word/_rels/document.xml.rels"] = """
<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.
org/package/2006/relationships">
<Relationship Target="numbering.xml" Id="docRId0" 
Type="http://schemas.openxmlformats.
org/officeDocument/2006/relationships/numbering"/>
<Relationship Target="styles.xml" Id="docRId1" 
Type="http://schemas.openxmlformats.
org/officeDocument/2006/relationships/styles"/>
</Relationships>
""" # noqa
Parts["_rels/.rels"] = """
<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.
org/package/2006/relationships">
<Relationship Target="word/document.xml" Id="pkgRId0" 
Type="http://schemas.openxmlformats.
org/officeDocument/2006/relationships/officeDocument"/></Relationships>
""" # noqa
