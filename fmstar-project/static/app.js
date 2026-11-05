// app.js - Compiled from app.ts for FMStar Front-End Engine

async function triggerLTXWorkflow() {
    const promptInput = document.getElementById('ltxPrompt');
    const ratioSelect = document.getElementById('ltxRatio');
    const profileSelect = document.getElementById('ltxAudioProfile');
    const statusBox = document.getElementById('ltxStatus');
    const videoPreview = document.getElementById('ltxVideoPreview');

    const prompt = promptInput ? promptInput.value.trim() : "";
    const ratio = ratioSelect ? ratioSelect.value : "16:9";
    const dspProfile = profileSelect ? profileSelect.value : "hybrid";

    if (!prompt) {
        alert('يرجى كتابة وصف المشهد السينمائي والصوتي أولاً!');
        return;
    }

    if (statusBox) {
        statusBox.innerText = '⏳ جاري إرسال الطلب إلى خادم LTX-2.5 وبدء المعالجة...';
        statusBox.style.color = 'var(--gold-accent)';
    }
    if (videoPreview) {
        videoPreview.style.display = 'none';
    }

    const payload = {
        prompt: prompt,
        ratio: ratio,
        dsp_profile: dspProfile
    };

    try {
        const response = await fetch('/api/fmstar/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.video_url) {
            if (statusBox) {
                statusBox.innerText = '✅ تم توليد المقطع والصوت بنجاح!';
                statusBox.style.color = '#00FF66';
            }

            if (videoPreview) {
                videoPreview.src = data.video_url;
                videoPreview.style.display = 'block';
                videoPreview.play().catch(() => {});
            }

            addPoints(100);
            showToast('تم التوليد بنجاح! 🎬', 'حصلت على 100 نقطة إضافية.', '+100 PTS');
        } else {
            if (statusBox) {
                statusBox.innerText = '❌ فشل التوليد: ' + (data.error || 'حدث خطأ في المعالجة.');
                statusBox.style.color = 'var(--alert-red)';
            }
        }
    } catch (err) {
        console.error('Error executing FMStar LTX pipeline:', err);
        if (statusBox) {
            statusBox.innerText = '❌ خطأ في الاتصال بالخادم الرئيسي.';
            statusBox.style.color = 'var(--alert-red)';
        }
    }
}

function addPoints(pts) {
    const ptsElem = document.getElementById('user-points');
    if (!ptsElem) return;

    let currentPts = parseInt(ptsElem.innerText.replace(/,/g, '')) || 0;
    currentPts += pts;
    ptsElem.innerText = currentPts.toLocaleString();
}

function showToast(title, desc, badgeText) {
    const toast = document.getElementById('rewardToast');
    const titleElem = document.getElementById('toastTitle');
    const descElem = document.getElementById('toastDesc');
    const badgeElem = document.getElementById('toastBadge');

    if (!toast) return;

    if (titleElem) titleElem.innerText = title;
    if (descElem) descElem.innerText = desc;
    if (badgeElem) badgeElem.innerText = badgeText;

    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function checkDailyStreak(manualCall = false) {
    if (manualCall) {
        addPoints(25);
        showToast('تسجيل الحضور اليومي! 🔥', 'تم الحفاظ على سلسلة الحضور بنجاح.', '+25 PTS');
    }
}

function openServiceModal(serviceName) {
    const modal = document.getElementById('serviceModalOverlay');
    const nameElem = document.getElementById('modalServiceName');
    if (nameElem) nameElem.innerText = `${serviceName} CONFIG`;
    if (modal) modal.classList.add('active');
}

function closeServiceModal(e) {
    const modal = document.getElementById('serviceModalOverlay');
    if (modal) modal.classList.remove('active');
}
