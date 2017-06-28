/**
 * Created by joe on 27.06.17.
 */
$(document).ready( function() {
$('body[data-catid="2"] .ppt_opc #wsd_checkout_form h3.amount_title span').text( function(index, text) {
	return text.replace('Spendenhöhe','jährliche Beitragshöhe');
});
});