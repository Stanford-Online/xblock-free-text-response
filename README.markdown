# FreeText XBlock
Enables instructors to create questions with free-text responses.

## TODO List:
- [ ] Write tests
- [ ] Update the `student_view`
    - [ ] `./xblockfreetext/private/view.html`
        - Add content to `<div class="xblockfreetext_block"></div>` element
    - [ ] `./xblockfreetext/private/view.js`
        - Add logic to `XblockFreetextView` function
    - [ ] `./xblockfreetext/private/view.less`
        - Add styles to `.xblockfreetext_block { }` block
    - [ ] `./xblockfreetext/xblockfreetext.py`
        - Add back-end logic to `student_view` method
- [ ] Update the `studio_view`
    - [ ] `./xblockfreetext/private/edit.html`
        - Add `<LI>` entries to `<ul class="list-input settings-list">` for each new field
    - [ ] `./xblockfreetext/private/edit.js`
        - Add entry for each field to `XblockFreetextEdit`
    - [ ] `./xblockfreetext/private/edit.less`
        - Add styles to `.xblockfreetext_edit { }` block (if needed)
    - [ ] `./xblockfreetext/xblockfreetext.py`
        - Add entry for each field to `studio_view_save`
- [ ] Update package metadata
    - [ ] `./package.json`
        - https://www.npmjs.org/doc/files/package.json.html
    - [ ] `./setup.py`
        - https://docs.python.org/2/distutils/setupscript.html#additional-meta-data
- [ ] Update `./Gruntfile.js`
    - http://gruntjs.com/getting-started
- [ ] Update `./README.markdown`
- [ ] Write documentation
- [ ] Publish on PyPi
