// app.ts - FMStar TypeScript Front-End Integration Engine

interface LTXGeneratePayload {
    prompt: string;
    ratio: string;
    dsp_profile: string;
}

interface LTXGenerateResponse {
    status: string;
    video_url?: string;
    error?: string;
}

async function triggerLTXWorkflow(): Promise<void> {
    const promptInput = document.getElementById('ltxPrompt') as HTMLTextAreaElement | null;
    const ratioSelect = document.getElementById('ltxRatio') as HTMLSelectElement | null;
    const profileSelect = document.getElementById('ltxAudioProfile') as HTMLSelectElement | null;
    const statusBox = document.getElementById('ltxStatus') as HTMLDivElement | null;
    const videoPreview = document.getElementById('ltxVideoPreview') as HTMLVideoElement | null;

    const prompt: string = promptInput ? promptInput.value.trim() : "";
    const ratio: string = ratioSelect ? ratioSelect.value : "16:9";
    const dspProfile: string = profileSelect ? profileSelect.value : "hybrid";

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

    const payload: LTXGeneratePayload = {
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

        const data: LTXGenerateResponse = await response.json();

        if (response.ok && data.video_url) {
            if (statusBox) {
                statusBox.innerText = '✅ تم توليد المقطع والصوت بنجاح!';
                statusBox.style.color = '#00FF66';
            }

            if (videoPreview) {
                videoPreview.src = data.video_url;
                videoPreview.style.display = 'block';
                videoPreview.play();
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

function addPoints(pts: number): void {
    const ptsElem = document.getElementById('user-points') as HTMLElement | null;
    if (!ptsElem) return;

    let currentPts: number = parseInt(ptsElem.innerText.replace(/,/g, '')) || 0;
    currentPts += pts;
    ptsElem.innerText = currentPts.toLocaleString();
}

function showToast(title: string, desc: string, badgeText: string): void {
    const toast = document.getElementById('rewardToast') as HTMLElement | null;
    const titleElem = document.getElementById('toastTitle') as HTMLElement | null;
    const descElem = document.getElementById('toastDesc') as HTMLElement | null;
    const badgeElem = document.getElementById('toastBadge') as HTMLElement | null;

    if (!toast) return;

    if (titleElem) titleElem.innerText = title;
    if (descElem) descElem.innerText = desc;
    if (badgeElem) badgeElem.innerText = badgeText;

    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function checkDailyStreak(manualCall: boolean = false): void {
    if (manualCall) {
        addPoints(25);
        showToast('تسجيل الحضور اليومي! 🔥', 'تم الحفاظ على سلسلة الحضور بنجاح.', '+25 PTS');
    }
}

function openServiceModal(serviceName: string): void {
    const modal = document.getElementById('serviceModalOverlay') as HTMLElement | null;
    const nameElem = document.getElementById('modalServiceName') as HTMLElement | null;
    if (nameElem) nameElem.innerText = `${serviceName} CONFIG`;
    if (modal) modal.classList.add('active');
}

function closeServiceModal(e?: Event): void {
    const modal = document.getElementById('serviceModalOverlay') as HTMLElement | null;
    if (modal) modal.classList.remove('active');
}
