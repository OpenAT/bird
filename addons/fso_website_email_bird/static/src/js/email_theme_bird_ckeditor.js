// CKEditor Settings
(function () {
    'use strict';
    // Overwrite class method of website/static/src/js/website.editor.js@839
    // to append/set/override CKEDITOR.config for wrapwrap editor
    openerp.website.RTE = openerp.website.RTE.extend({
        _config: function () {
            // Run the original method to modify it's result
            var config =  this._super();

            // Set custom toolbar
            // https://docs.ckeditor.com/ckeditor4/latest/guide/dev_toolbar.html
            config.toolbar = [{
                name: 'basicstyles', items: [
                    "Bold", "Italic", "Underline", "Strike", "Subscript",
                    "Superscript", "TextColor", "BGColor", "RemoveFormat"
                ]
            }, {
                name: 'span', items: [
                    "Link", "Blockquote", "BulletedList",
                    "NumberedList", "Indent", "Outdent"
                ]
            }, {
                name: 'justify', items: [
                    "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock"
                ]
            }, {
                name: 'special', items: [
                    "Image"
                ]
            }, {
                name: 'styles', items: [
                    "Styles",
                ]
            }
            ];

            // Add Custom font and font background colors
            config.colorButton_colors = 'ffffff,555555,000000,cccccc,b32986,f49800,407cca,57c940,c9c940,c94740';
            // config.colorButton_colorsPerRow = 4;
            // config.colorButton_enableAutomatic = true;


            // styles dropdown in toolbar
            config.stylesSet = [
                {name: 'Normal', element: 'p'},
                {name: 'Small', element: 'p', attributes: { 'class': 'bird_small_text' } },
                {name: 'H1 42', element: 'h1'},
                {name: 'H1 40', element: 'h1', attributes: { 'class': 'bird_h1_40' } },
                {name: 'H2 26', element: 'h2'},
                {name: 'H3 22', element: 'h3'},
                {name: 'H4 20', element: 'h4'},
                {name: 'H5 18', element: 'h5'},
                {name: 'H6 16', element: 'h6'},
                {name: 'Formatted', element: 'pre'},
                {name: 'Address', element: 'address'},
                {name: 'Date in H1-6', element: 'span', attributes: { 'class': 'bird_date_in_header' } },
            ];

            // return the config
            return config;
        }
    });
})();
