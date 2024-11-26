document.addEventListener("DOMContentLoaded", function () {
    // Parse the JSON data
    // products is parsed in the html using jinja + tojson 
    let productsPerPage = parseInt(document.getElementById("products-per-page").value, 10); //default is 10
    let currentPage = 1;
    let sortOrder = "a-to-z"; // Default sort order

    // Get HTML elements
    const productContainer = document.getElementById("product-container");
    const prevPageButton = document.getElementById("prev-page");
    const nextPageButton = document.getElementById("next-page");
    const pageInfo = document.getElementById("page-info");
    const productsPerPageSelect = document.getElementById("products-per-page");
    const sortBySelect = document.getElementById("sort-by");

    // Function to sort products
    function sortProducts(products, order) 
    {
        // Create a copy of the products array
        const sortedProducts = products.slice(); 

        // bubble sort depending on sorting parameter
        for (let i = 0; i < sortedProducts.length - 1; i++) {
            for (let j = 0; j < sortedProducts.length - i - 1; j++) {
                if (order === "low-to-high") {
                    if (sortedProducts[j].price > sortedProducts[j + 1].price) {
                        const temp = sortedProducts[j];
                        sortedProducts[j] = sortedProducts[j + 1];
                        sortedProducts[j + 1] = temp;
                    }
                }
                else if (order === "high-to-low") {
                    if (sortedProducts[j].price < sortedProducts[j + 1].price) {
                        const temp = sortedProducts[j];
                        sortedProducts[j] = sortedProducts[j + 1];
                        sortedProducts[j + 1] = temp;
                    }
                }
                else if (order === "a-to-z") {
                    if (sortedProducts[j].name.toLowerCase() > sortedProducts[j + 1].name.toLowerCase()) {
                        const temp = sortedProducts[j];
                        sortedProducts[j] = sortedProducts[j + 1];
                        sortedProducts[j + 1] = temp;
                    }
                }
            }
        }
        return sortedProducts;
    }

    // Function to render products on the page
    function renderProducts() {
        //sort the products to display
        const sortedProducts = sortProducts(products, sortOrder);
        //setup how many products are to be displayed per page
        productContainer.innerHTML = "";
        var startIndex = (currentPage - 1) * productsPerPage;
        var endIndex = startIndex + productsPerPage;
        // create array from sorted that are for that page only
        const productsToDisplay = sortedProducts.slice(startIndex, endIndex);

        // Display products as cards
        for (var i = 0; i < productsToDisplay.length; i++) {
            var product = productsToDisplay[i];
            var productCard = document.createElement("div");
            productCard.classList.add("product-card");
            productCard.innerHTML = `
                <a href = "/product/${product.id}" style="text-decoration: none; color: inherit;">                
                <h3>${product.name}</h3>
                <img src="/static/images/${product.img}" class="card-img-top" alt="[image of ${product.name}]">
                <p>${product.description}</p>
                <p>Price: $${product.price.toFixed(2)}</p>
                <p>${product.stock > 0 && `In Stock: ${product.stock}` || "Out of Stock"}</p>
                </p>
            `;
            productContainer.appendChild(productCard);
        }

        // Update pagination info and button states
        pageInfo.textContent = "Page " + currentPage + " of " + Math.ceil(products.length / productsPerPage);
        // Disable the previous button if on the first page
        if (currentPage <= 1) {
            prevPageButton.disabled = true;
        } else {
            prevPageButton.disabled = false;
        }

        // Disable the next button if on the last page
        var totalPages = Math.floor(products.length / productsPerPage);
        // Add an extra page for leftover products
        if (products.length % productsPerPage !== 0) {
            totalPages++;
        }
        if (currentPage >= totalPages) {
            nextPageButton.disabled = true;
        } else {
            nextPageButton.disabled = false;
        }

    }

    //event listener for when previous page button is clicked
    prevPageButton.addEventListener("click", function () {
        if (currentPage > 1) {
            currentPage--;
            renderProducts();
        }
    });

    //event listener for when next page button is clicked
    nextPageButton.addEventListener("click", function () {
        if (currentPage < Math.ceil(products.length / productsPerPage)) {
            currentPage++;
            renderProducts();
        }
    });

    // Event listener for changes in the products per page input
    productsPerPageSelect.addEventListener("change", function () {
        productsPerPage = parseInt(this.value); // Update products per page
        // Reset to the first page
        currentPage = 1; 
        renderProducts();
    });

    // Event listener for changes in the Sort by dropdown
    sortBySelect.addEventListener("change", function () {
        // Update the sort order
        sortOrder = this.value;
        // Reset to the first page 
        currentPage = 1; 
        renderProducts();
    });
    
    //inital render
    renderProducts();
});
