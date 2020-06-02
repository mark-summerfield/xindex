#!/bin/bash
tokei -s lines -f -t=Python -e*test*.py -eIcons.py -einfo -emisc \
    -ebin -etests -eQrc.py -e*setup*.py -e*dump*.py -eMakeTestXix.py \
    -egenerated-lout2ximl.py
./tests/all.py
unrecognized.py -q
flake . \
    | grep -v 'Lib/__init__.py.*maybe_register_filetype.*unused'
python3 -m vulture . \
    | grep -v 'Actions/File.py.*Unused.attribute..Printer' \
    | grep -v 'Const/Kinds.py.*Unused.variable..[A-Z]' \
    | grep -v Unused.variable..exc_[tv] \
    | grep -v 'Unused.attribute....[gs]type' \
    | grep -v ^tests/ \
    | grep -v 'Actions/File.py.*Unused.attribute..Printer' \
    | grep -v 'Select.*.py.*Unused.variable..[A-Z]' \
    | grep -v 'Forms/CopyCharacter.py.*Unused.function.*mouseMoveEvent' \
    | grep -v 'Forms/.*Options.py.*Unused.attribute.*ed' \
    | grep -v 'HelpForm.py.*Unused.function.*hideEvent' \
    | grep -v 'Unused.function.*handle_.*' \
    | grep -v 'Pages/Page.py.*Unused.attribute.*numeric' \
    | grep -v 'Spell.*.py.*Unused.*language' \
    | grep -v 'State.py.*Unused.attribute.*spell' \
    | grep -v 'Views.*.py.*Unused.function.*Event' \
    | grep -v 'Widgets/AlphaBar.py.*Unused.function.*contextMenuEvent' \
    | grep -v 'Widgets/AlphaBar.py.*Unused.function.*heightForWidth' \
    | grep -v 'Widgets/ChangeSpinBox.py.*Unused.function.*valueFromText' \
    | grep -v 'Widgets/ChangeSpinBox.py.*Unused.function.*textFromValue' \
    | grep -v 'Widgets/Label.py.*Unused.function.*changeEvent' \
    | grep -v 'Widgets/LineEdit/HtmlLineEdit.py.*Unused.function.*highlightBlock' \
    | grep -v 'Widgets/LineEdit/HtmlLineEdit.py.*Unused.attribute.*spaceHighlighter' \
    | grep -v 'Widgets/List.py.*Unused.function.*paint' \
    | grep -v 'Widgets/RomanSpinBox.py.*Unused.function.*valueFromText' \
    | grep -v 'Widgets/RomanSpinBox.py.*Unused.function.*textFromValue' \
    | grep -v 'Widgets/SpellHighlighter.py.*Unused.function.*highlightBlock' \
    | grep -v 'Widgets/Splitter.py.*Unused.function.*createHandle' \
    | grep -v 'Window/Window.py.*Unused.attribute.*DEBUGGING' \
    | grep -v 'Xix/_XixImport.*.py.*Unused.attribute.*inFont' \
    | grep -v 'Xix/Command.py.*Unused.attribute.*to_term' \
    | grep -v 'Qrc.py' \
    | grep -v 'Unused.import..Qrc'
wc -w t2t/*.t2t|tail -n 1
git status
