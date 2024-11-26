$(document).ready(function () {
    const csrfToken = $("input[name='csrf_token']").val(); // Fetch the CSRF token from the page

    // Function to recalculate and update the basket total
    function updateBasketTotal() {
        // Initialize total to 0
        let total = 0;

        // Loop through each row to calculate the total sum
        $(".total").each(function () {
            total += parseFloat($(this).text().replace("£", ""));
        });

        // Update the total display in the basket summary
        $(".basket-total").text(`Total Cost: £${total.toFixed(2)}`);
    }

    // Handle quantity changes
    $(".quantity-input").on("change", function () {
        // Get information required (product id and changed quantity)
        var inputElement = $(this);
        var productId = String(inputElement.data("product-id"));
        var newQuantity = parseInt(inputElement.val());

        // Ensure the quantity is within bounds
        var maxQuantity = parseInt(inputElement.attr("max"));
        var minQuantity = parseInt(inputElement.attr("min"));
        if (newQuantity < minQuantity) {
            inputElement.val(minQuantity);
            return;
        }
        if (newQuantity > maxQuantity) {
            inputElement.val(maxQuantity);
            return;
        }

        // Send POST request to edit the product quantity in basket
        $.ajax({
            url: "/update-basket",
            type: "POST",
            headers: {
                "X-CSRFToken": csrfToken 
            },
            data: JSON.stringify({ product_id: productId, quantity: newQuantity }),
            contentType: "application/json",
            dataType: "json",
            csrf_token: csrfToken,
            success: function (response) {
                // If successful response then recalculate the prices and change dynamically
                var row = $(`tr[data-product-id="${productId}"]`);
                var price = parseFloat(row.find(".price").text().replace("£", ""));
                row.find(".total").text(`£${(price * newQuantity).toFixed(2)}`);
                // Update the basket total
                updateBasketTotal();
            },
        });

    });

    // Handle product deletion
    $(".delete-btn").on("click", function () {
        // Get product id from button data
        var buttonElement = $(this);
        var productId = String(buttonElement.data("product-id"));

        // Send POST request to remove the product from basket
        $.ajax({
            url: "/delete-from-basket",
            type: "POST",
            headers: {
                "X-CSRFToken": csrfToken 
            },
            data: JSON.stringify({ product_id: productId }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                // If successful response then delete row of that product
                var row = $(`tr[data-product-id="${productId}"]`);
                row.remove();
                // Update the basket total
                updateBasketTotal();
                // If no items in basket then remove table, buttons and show empty basket message
                if ($("tbody tr").length === 0) {
                    $(".basket-table").remove();
                    $(".basket-actions").remove();
                    $(".empty-basket-message").removeClass("d-none");
                }
            },
        });

    });

    // Initial total calculation on page load
    updateBasketTotal();
});
