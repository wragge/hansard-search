$(function () {
    $('#datepicker1').datetimepicker({
        format: 'YYYY-MM-DD',
        // defaultDate: '1901-01-01'
    });
    $('#datepicker2').datetimepicker({
        format: 'YYYY-MM-DD',
        // defaultDate: '1980-12-31'
    });

    function validateEmail() {
        var email = $("#email").val();
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
    $('form').submit(function(event) {
        if (validateEmail() === true) {
            return;
        }
        $("#email").parent().addClass('has-error');
        $("#email").focus();
        event.preventDefault();
    });
    $("#email").focus();
});