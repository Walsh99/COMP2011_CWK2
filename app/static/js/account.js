// simple javascript to toggle the new password forms if option checked
function togglePasswordFields() 
{
    const passwordFields = document.querySelectorAll('.password-fields');
    for (let i = 0; i < passwordFields.length; i++) 
    {
        passwordFields[i].classList.toggle('d-none');
    }
}
