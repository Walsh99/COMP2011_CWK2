$(document).ready(function () 
{
    $("#submit-review").on("click", function (event) 
    {
        // Prevent form submission so doesnt reload page
        event.preventDefault();

        // get values of product to be reviewed, rating and comment (val retrieves input, trim removes whitespace)
        var productId = $("input[name='product_id']").val();
        var rating = $("#rating").val();
        var comment = $("#comment").val().trim();
        var csrfToken = $("input[name='csrf_token']").val(); // Get CSRF token from the form

        // Basic validation, chose to use this over forms.py as only 1 thing of validation needed
        if (!comment) 
        {
            alert("Please enter a Comment.");
            return;
        }

        // AJAX POST request to submit a review
        $.ajax({
            url: "/add-review",
            type: "POST",
            data: {
                product_id: productId,
                rating: rating,
                comment: comment,
                csrf_token: csrfToken // Include CSRF token in the request data
            },
            // if successful then use response to dynammicaly change the reviews
            success: function (response) 
            {
                // Clear the form fields
                $("#rating").val("1");
                $("#comment").val("");
                // Add the new review dynamically to the  list
                $("#reviews-list").prepend(`
                    <li>
                        <strong>${response.first_name} ${response.last_name}</strong> 
                        rated <strong>${response.rating}/5</strong>
                        <p>${response.comment}</p>
                        <small>${response.created_at}</small>
                    </li>
                `);
            }
        });
    });
});
