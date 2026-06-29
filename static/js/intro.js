document.addEventListener("DOMContentLoaded", function () {
    const introScreen = document.getElementById("intro-screen");
    const introLogo = document.getElementById("introLogo");
    const mainLogo = document.getElementById("mainLogo");
    const mainContents = document.querySelectorAll(".main-content");
    const skipBtn = document.getElementById("intro-skip-btn");

    if (!introScreen || !introLogo || !mainLogo) {
        return;
    }

    function showMainContent() {
        mainContents.forEach(function (content) {
            content.classList.add("show");
        });
    }

    /*
        이미 인트로를 본 적 있으면
        인트로 화면을 바로 숨기고 메인화면만 보여줌
    */
    if (sessionStorage.getItem("introPlayed") === "true") {
        introScreen.style.display = "none";

        mainLogo.classList.add("show");
        mainLogo.style.opacity = "1";

        showMainContent();

        return;
    }

    /*
        처음 접속이면 인트로 실행 기록 저장
    */
    sessionStorage.setItem("introPlayed", "true");

    // 메인 navbar 로고는 인트로 중 숨김
    mainLogo.classList.remove("show");
    mainLogo.style.opacity = "0";

    function revealIntroLogo() {
        introLogo.classList.add("logo-show");
    }

    function flyLogoToNavbar() {
        const targetRect = mainLogo.getBoundingClientRect();
        const currentRect = introLogo.getBoundingClientRect();

        // 현재 화면상의 위치를 inline style로 고정
        introLogo.classList.remove("logo-show");

        introLogo.style.left = currentRect.left + "px";
        introLogo.style.top = currentRect.top + "px";
        introLogo.style.width = currentRect.width + "px";
        introLogo.style.transform = "translate(0, 0)";
        introLogo.style.opacity = "1";

        // 브라우저가 현재 위치를 먼저 인식하게 함
        introLogo.offsetHeight;

        // transition 활성화
        introLogo.classList.add("logo-fly");

        // 실제 navbar 로고 위치로 이동
        introLogo.style.left = targetRect.left + "px";
        introLogo.style.top = targetRect.top + "px";
        introLogo.style.width = targetRect.width + "px";
        introLogo.style.transform = "translate(0, 0)";

        setTimeout(function () {
            // 실제 navbar 로고 표시
            mainLogo.classList.add("show");
            mainLogo.style.opacity = "1";

            // 인트로 로고 제거
            introLogo.style.opacity = "0";

            // 메인 콘텐츠 표시
            showMainContent();

            // 인트로 화면 fade out
            introScreen.classList.add("hide");

            setTimeout(function () {
                introScreen.style.display = "none";
            }, 800);

        }, 1000);
    }

    const revealTimer = setTimeout(revealIntroLogo, 3600);
    const flyTimer = setTimeout(flyLogoToNavbar, 5000);

    if (skipBtn) {
        skipBtn.addEventListener("click", function () {
            clearTimeout(revealTimer);
            clearTimeout(flyTimer);

            introLogo.classList.add("logo-show");

            setTimeout(function () {
                flyLogoToNavbar();
            }, 100);
        });
    }
});