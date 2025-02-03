let currentPage = 1;
const productsPerPage = 53;
let allProducts = [];


// ✅ البحث عن المنتجات
function searchProducts() {
    const keyword = document.getElementById('keyword').value;
    const pages = parseInt(document.getElementById('pages').value);
    const sortBy = document.getElementById('sortBy').value;

    if (!keyword || isNaN(pages) || pages < 1) {
        alert("Please enter a valid keyword and number of pages.");
        return;
    }

    document.getElementById('results').innerHTML = "<p>Loading...</p>";

    // ✅ إرسال الكلمات المفتاحية إلى الخادم لمعالجة المرادفات
    fetch('https://amazon-scraper-lx5h.onrender.com/scrape', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword, pages }) // يتم إرسال الكلمة الرئيسية هنا
    })
    .then(response => response.json())
    .then(data => {
        allProducts = data;
        currentPage = 1;
        sortResults(sortBy);
        displayResults();
        setupPagination();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = "<p>Failed to load data.</p>";
    });
}

// ✅ عرض المنتجات
function displayResults() {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    const start = (currentPage - 1) * productsPerPage;
    const end = start + productsPerPage;
    const productsToShow = allProducts.slice(start, end);

    productsToShow.forEach(product => {
        const card = document.createElement('div');
        card.classList.add('product-card');

        card.innerHTML = `
            <img src="${product.image}" alt="Product Image">
            <div class="product-info">
                <h3>${product.title}</h3>
                <p><strong>ASIN:</strong> ${product.asin}</p>
                <p><strong>BSR:</strong> ${product.bsr && product.bsr.length > 0 ? product.bsr.join(', ') : 'N/A'}</p>
                <p><strong>Rating:</strong> ⭐ ${product.ratings || '0'}</p>
                <p><strong>Date Published:</strong> ${product.date_published || 'N/A'}</p>
                <a href="${product.link}" target="_blank" class="view-link">View on Amazon</a>
            </div>
        `;

        resultsContainer.appendChild(card);
    });
}

// ✅ إعداد التنقل بين الصفحات
function setupPagination() {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    const totalPages = Math.ceil(allProducts.length / productsPerPage);

    const prevButton = document.createElement('button');
    prevButton.textContent = 'Previous';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => {
        currentPage--;
        displayResults();
        setupPagination();
    };

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Next';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => {
        currentPage++;
        displayResults();
        setupPagination();
    };

    paginationContainer.appendChild(prevButton);
    paginationContainer.appendChild(document.createTextNode(` Page ${currentPage} of ${totalPages} `));
    paginationContainer.appendChild(nextButton);
}

// ✅ تصدير ASIN فقط إلى ملف CSV
function exportASINs() {
    if (allProducts.length === 0) {
        alert("No products to export.");
        return;
    }

    let csvContent = "ASIN\n";
    allProducts.forEach(product => {
        csvContent += `${product.asin}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'amazon_asins.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ✅ نظام الفرز (BSR - Rating - Date)
function sortResults(sortBy) {
    if (allProducts.length === 0) return;

    allProducts.sort((a, b) => {
        let valueA, valueB;

        if (sortBy === 'bsr-asc') {
            valueA = parseInt(a.bsr?.[0]?.replace(/\D/g, '') || Infinity);
            valueB = parseInt(b.bsr?.[0]?.replace(/\D/g, '') || Infinity);
            return valueA - valueB;
        } 
        else if (sortBy === 'bsr-desc') {
            valueA = parseInt(a.bsr?.[0]?.replace(/\D/g, '') || Infinity);
            valueB = parseInt(b.bsr?.[0]?.replace(/\D/g, '') || Infinity);
            return valueB - valueA;
        } 
        else if (sortBy === 'rating-asc') {
            valueA = parseFloat(a.ratings) || 0;
            valueB = parseFloat(b.ratings) || 0;
            return valueA - valueB;
        } 
        else if (sortBy === 'rating-desc') {
            valueA = parseFloat(a.ratings) || 0;
            valueB = parseFloat(b.ratings) || 0;
            return valueB - valueA;
        }

        return 0;
    });

    displayResults();
    setupPagination();
}
