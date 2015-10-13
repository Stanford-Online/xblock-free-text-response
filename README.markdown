# FreeText XBlock
Enables instructors to create questions with free-text responses.

## TODO List:
- [ ] Write tests
- [ ] Update the `student_view`
    - [ ] `./freetextresponse/private/view.html`
        - Add content to `<div class="freetextresponse_block"></div>` element
    - [ ] `./freetextresponse/private/view.js`
        - Add logic to `FreetextresponseView` function
    - [ ] `./freetextresponse/private/view.less`
        - Add styles to `.freetextresponse_block { }` block
    - [ ] `./freetextresponse/freetextresponse.py`
        - Add back-end logic to `student_view` method
- [ ] Update the `studio_view`
    - [ ] `./freetextresponse/private/edit.html`
        - Add `<LI>` entries to `<ul class="list-input settings-list">` for each new field
    - [ ] `./freetextresponse/private/edit.js`
        - Add entry for each field to `FreetextResponseEdit`
    - [ ] `./freetextresponse/private/edit.less`
        - Add styles to `.freetextresponse_edit { }` block (if needed)
    - [ ] `./freetextresponse/freetextresponse.py`
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
