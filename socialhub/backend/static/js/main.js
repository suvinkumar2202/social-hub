document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
        || getCookie('csrftoken');

    function getCookie(name) {
        let value = null;
        document.cookie.split(';').forEach(c => {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                value = decodeURIComponent(c.substring(name.length + 1));
            }
        });
        return value;
    }

    function ajaxPost(url, data, callback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data,
        })
        .then(r => r.json())
        .then(callback)
        .catch(err => console.error(err));
    }

    // Mobile nav toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
        // Close nav when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
            }
        });
    }

    // Like buttons
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const url = this.dataset.url;
            const btnEl = this;
            ajaxPost(url, '', (data) => {
                if (data.liked) {
                    btnEl.classList.add('liked');
                    btnEl.querySelector('.action-icon').innerHTML = '\u2665';
                    btnEl.style.transform = 'scale(1.2)';
                    setTimeout(() => { btnEl.style.transform = 'scale(1)'; }, 200);
                } else {
                    btnEl.classList.remove('liked');
                    btnEl.querySelector('.action-icon').innerHTML = '\u2661';
                }
                btnEl.querySelector('.like-count').textContent = data.like_count;
            });
        });
    });

    // Toggle comments
    document.querySelectorAll('.comment-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const postId = this.dataset.postId;
            const section = document.getElementById('comments-' + postId);
            if (section) {
                const isVisible = section.style.display !== 'none';
                section.style.display = isVisible ? 'none' : 'block';
                if (!isVisible) {
                    const input = section.querySelector('.comment-input');
                    if (input) input.focus();
                }
            }
        });
    });

    // Comment forms
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const input = this.querySelector('.comment-input');
            const url = this.action;
            const content = input.value.trim();
            if (!content) return;

            const submitBtn = this.querySelector('button[type=submit]');
            submitBtn.disabled = true;

            ajaxPost(url, 'content=' + encodeURIComponent(content), (data) => {
                if (data.success) {
                    const commentsList = this.previousElementSibling;
                    const div = document.createElement('div');
                    div.className = 'comment-item';
                    div.style.opacity = '0';
                    div.style.transform = 'translateY(-8px)';
                    div.innerHTML = `
                        <div class="comment-content">
                            <a href="/profile/${data.username}/" class="comment-author">${escapeHtml(data.username)}</a>
                            <span class="comment-text">${escapeHtml(data.content)}</span>
                        </div>
                    `;
                    commentsList.appendChild(div);
                    requestAnimationFrame(() => {
                        div.style.transition = 'all 0.3s';
                        div.style.opacity = '1';
                        div.style.transform = 'translateY(0)';
                    });
                    input.value = '';

                    const postCard = this.closest('.post-card') || this.closest('.profile-tab-content');
                    const countEl = postCard?.querySelector('.comment-count');
                    if (countEl) countEl.textContent = data.comment_count;
                }
                submitBtn.disabled = false;
            });
        });
    });

    // Delete comment
    document.querySelectorAll('.delete-comment-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const url = this.dataset.url;
            const commentEl = this.closest('.comment-item');
            ajaxPost(url, '', (data) => {
                if (data.success) {
                    commentEl.style.opacity = '0';
                    commentEl.style.transform = 'translateX(-10px)';
                    commentEl.style.transition = 'all 0.3s';
                    setTimeout(() => {
                        commentEl.remove();
                        const postCard = commentEl.closest('.post-card');
                        if (postCard) {
                            const countEl = postCard.querySelector('.comment-count');
                            if (countEl) countEl.textContent = data.comment_count;
                        }
                    }, 300);
                }
            });
        });
    });

    // Follow/unfollow
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const url = this.dataset.url;
            const btnEl = this;
            ajaxPost(url, '', (data) => {
                if (data.following !== undefined) {
                    if (data.following) {
                        btnEl.textContent = 'Following';
                        btnEl.classList.add('following');
                    } else {
                        btnEl.textContent = 'Follow';
                        btnEl.classList.remove('following');
                    }

                    document.querySelectorAll('.stat').forEach(stat => {
                        if (stat.textContent.includes('followers')) {
                            const strong = stat.querySelector('strong');
                            if (strong) strong.textContent = data.follower_count;
                        }
                    });
                }
            });
        });
    });

    // Delete post
    document.querySelectorAll('.delete-post-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!confirm('Delete this post? This cannot be undone.')) return;
            const postCard = this.closest('.post-card') || this.closest('article');
            ajaxPost(this.action, '', (data) => {
                if (data.success) {
                    postCard.style.opacity = '0';
                    postCard.style.transform = 'scale(0.96)';
                    postCard.style.transition = 'all 0.3s';
                    setTimeout(() => postCard.remove(), 300);
                }
            });
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
