
const API_BASE = "http://127.0.0.1:8000";

let books = [];
let members = [];
let issues = [];

// ---------- Common helpers ----------

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function showMessage(message, isError = false) {
    const element = document.getElementById("message");
    element.textContent = message;
    element.className = isError ? "error" : "success";
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        try {
            const errorData = await response.json();
            message = errorData.detail || message;
        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

// ---------- Navigation ----------

function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(section => {
        section.classList.add("hidden");
    });

    document.getElementById(sectionId).classList.remove("hidden");

    if (sectionId === "books") renderBooks();
    if (sectionId === "members") renderMembers();
    if (sectionId === "issues") renderIssues();
}

// ---------- Load data from FastAPI ----------

async function loadAll() {
    try {
        const [bookData, memberData, issueData] = await Promise.all([
            apiRequest("/Books"),
            apiRequest("/Members"),
            apiRequest("/Issues")
        ]);

        books = bookData;
        members = memberData;
        issues = issueData;

        document.getElementById("totalBooks").textContent = books.length;
        document.getElementById("totalMembers").textContent = members.length;
        document.getElementById("totalIssues").textContent = issues.length;
        document.getElementById("availableBooks").textContent =
            books.length - issues.length;

        renderRecentBooks();
        renderBooks();
        renderMembers();
        renderIssues();

        showMessage("Data loaded successfully.");
    } catch (error) {
        showMessage(
            `Could not load data. Check that FastAPI is running. ${error.message}`,
            true
        );
    }
}

// ---------- Dashboard ----------

function renderRecentBooks() {
    const tbody = document.getElementById("recentBooks");

    tbody.innerHTML = books.slice(-5).reverse().map(book => `
        <tr>
            <td>${book.id}</td>
            <td>${escapeHTML(book.title)}</td>
            <td>${escapeHTML(book.author)}</td>
        </tr>
    `).join("");

    if (!books.length) {
        tbody.innerHTML = `<tr><td colspan="3">No books found.</td></tr>`;
    }
}

// ---------- Book management ----------

function renderBooks() {
    const tbody = document.getElementById("booksTable");
    const search = (
        document.getElementById("bookSearch")?.value || ""
    ).trim().toLowerCase();

    const filteredBooks = books.filter(book =>
        String(book.id).includes(search) ||
        book.title.toLowerCase().includes(search) ||
        book.author.toLowerCase().includes(search)
    );

    tbody.innerHTML = filteredBooks.map(book => `
        <tr>
            <td>${book.id}</td>
            <td>${escapeHTML(book.title)}</td>
            <td>${escapeHTML(book.author)}</td>
            <td>
                <button class="edit-btn"
                    onclick="editBook(${book.id})">Edit</button>
                <button class="delete-btn"
                    onclick="deleteBook(${book.id})">Delete</button>
            </td>
        </tr>
    `).join("");

    if (!filteredBooks.length) {
        tbody.innerHTML = `<tr><td colspan="4">No books found.</td></tr>`;
    }
}

function resetBookForm() {
    document.getElementById("bookForm").reset();
    document.getElementById("bookId").value = "";
    document.getElementById("bookFormTitle").textContent = "Add Book";
}

function editBook(id) {
    const book = books.find(item => item.id === id);
    if (!book) return;

    document.getElementById("bookId").value = book.id;
    document.getElementById("bookTitle").value = book.title;
    document.getElementById("bookAuthor").value = book.author;
    document.getElementById("bookFormTitle").textContent = "Edit Book";

    showSection("books");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.getElementById("bookForm").addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("bookId").value;
    const payload = {
        title: document.getElementById("bookTitle").value.trim(),
        author: document.getElementById("bookAuthor").value.trim()
    };

    try {
        if (id) {
            await apiRequest(`/Books/${id}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
            showMessage("Book updated successfully.");
        } else {
            await apiRequest("/Books", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            showMessage("Book added successfully.");
        }

        resetBookForm();
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
});

async function deleteBook(id) {
    if (!confirm("Are you sure you want to delete this book?")) return;

    try {
        await apiRequest(`/Books/${id}`, { method: "DELETE" });
        showMessage("Book deleted successfully.");
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
}

document.getElementById("bookSearch").addEventListener("input", renderBooks);

// ---------- Member management ----------

function renderMembers() {
    const tbody = document.getElementById("membersTable");
    const search = (
        document.getElementById("memberSearch")?.value || ""
    ).trim().toLowerCase();

    const filteredMembers = members.filter(member =>
        String(member.id).includes(search) ||
        member.name.toLowerCase().includes(search)
    );

    tbody.innerHTML = filteredMembers.map(member => `
        <tr>
            <td>${member.id}</td>
            <td>${escapeHTML(member.name)}</td>
            <td>
                <button class="edit-btn"
                    onclick="editMember(${member.id})">Edit</button>
                <button class="delete-btn"
                    onclick="deleteMember(${member.id})">Delete</button>
            </td>
        </tr>
    `).join("");

    if (!filteredMembers.length) {
        tbody.innerHTML = `<tr><td colspan="3">No members found.</td></tr>`;
    }
}

function resetMemberForm() {
    document.getElementById("memberForm").reset();
    document.getElementById("memberId").value = "";
    document.getElementById("memberFormTitle").textContent = "Add Member";
}

function editMember(id) {
    const member = members.find(item => item.id === id);
    if (!member) return;

    document.getElementById("memberId").value = member.id;
    document.getElementById("memberName").value = member.name;
    document.getElementById("memberFormTitle").textContent = "Edit Member";

    showSection("members");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.getElementById("memberForm").addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("memberId").value;
    const name = document.getElementById("memberName").value.trim();

    if (!name) {
        showMessage("Please enter a member name.", true);
        return;
    }

    try {
        if (id) {
            await apiRequest(`/Members/${id}`, {
                method: "PUT",
                body: JSON.stringify({ name })
            });
            showMessage("Member updated successfully.");
        } else {
            await apiRequest("/Members", {
                method: "POST",
                body: JSON.stringify({ name })
            });
            showMessage("Member added successfully.");
        }

        resetMemberForm();
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
});

async function deleteMember(id) {
    if (!confirm("Are you sure you want to delete this member?")) return;

    try {
        await apiRequest(`/Members/${id}`, { method: "DELETE" });
        showMessage("Member deleted successfully.");
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
}

document.getElementById("memberSearch").addEventListener("input", renderMembers);

// ---------- Issue and return books ----------

function renderIssues() {
    const tbody = document.getElementById("issuesTable");

    tbody.innerHTML = issues.map(issue => {
        const member = members.find(item => item.id === issue.member_id);
        const book = books.find(item => item.id === issue.book_id);

        return `
            <tr>
                <td>${issue.id}</td>
                <td>${issue.member_id} - ${escapeHTML(member?.name || "Unknown")}</td>
                <td>${issue.book_id} - ${escapeHTML(book?.title || "Unknown")}</td>
                <td>
                    <button class="return-btn"
                        onclick="returnBook(${issue.id})">Return</button>
                </td>
            </tr>
        `;
    }).join("");

    if (!issues.length) {
        tbody.innerHTML = `<tr><td colspan="4">No books are currently issued.</td></tr>`;
    }
}

document.getElementById("issueForm").addEventListener("submit", async event => {
    event.preventDefault();

    const memberId = Number(document.getElementById("issueMemberId").value);
    const bookId = Number(document.getElementById("issueBookId").value);

    try {
        await apiRequest("/Issues", {
            method: "POST",
            body: JSON.stringify({
                member_id: memberId,
                book_id: bookId
            })
        });

        document.getElementById("issueForm").reset();
        showMessage("Book issued successfully.");
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
});

async function returnBook(issueId) {
    if (!confirm("Confirm that this book is being returned?")) return;

    try {
        await apiRequest(`/Issues/${issueId}`, { method: "DELETE" });
        showMessage("Book returned successfully.");
        await loadAll();
    } catch (error) {
        showMessage(error.message, true);
    }
}

// Load the dashboard when the page opens.
loadAll();
