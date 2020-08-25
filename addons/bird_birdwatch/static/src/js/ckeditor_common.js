(function () {
    'use strict';

    openerp.website.EditorBar.include({

        edit: function () {
            console.log('Empty #bird_birdwatch_map on edit!');
            $('#bird_birdwatch_map').empty();
            return this._super.apply(this, arguments);
        },

        save: function () {
            console.log('Empty #bird_birdwatch_map on save!');
            $('#bird_birdwatch_map').empty();
            // this._super();
            return this._super.apply(this, arguments);
        },
    });

})();
