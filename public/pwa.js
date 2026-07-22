/* Texas CNA Academy — PWA bootstrap: service worker registration + home-screen install prompt. */
(function () {
  'use strict';

  var DISMISS_KEY = 'tca-pwa-install-dismissed-at';
  var DISMISS_DAYS = 14;

  function isStandalone() {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    );
  }

  function isIos() {
    var ua = window.navigator.userAgent;
    var isAppleMobile = /iphone|ipad|ipod/i.test(ua) ||
      (/macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
    return isAppleMobile && !/crios|fxios|edgios/i.test(ua);
  }

  function recentlyDismissed() {
    try {
      var at = Number(window.localStorage.getItem(DISMISS_KEY));
      return at && Date.now() - at < DISMISS_DAYS * 24 * 60 * 60 * 1000;
    } catch (err) {
      return false;
    }
  }

  function rememberDismissed() {
    try {
      window.localStorage.setItem(DISMISS_KEY, String(Date.now()));
    } catch (err) { /* private mode: ignore */ }
  }

  /* Register the app-shell service worker for offline support. */
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/service-worker.js').catch(function () {
        /* Registration failures (e.g. unsupported scope) are non-fatal. */
      });
    });
  }

  if (isStandalone() || recentlyDismissed()) return;

  var deferredPrompt = null;
  var banner = null;

  function buildBanner(bodyHtml, actionsHtml) {
    var el = document.createElement('div');
    el.id = 'tca-pwa-banner';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-label', 'Install Texas CNA Academy');
    el.innerHTML =
      '<style>' +
      '#tca-pwa-banner{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;' +
      'background:#0B1D35;color:#F5EDE0;border:1px solid #C8971A;border-radius:10px;' +
      'box-shadow:0 8px 30px rgba(11,29,53,0.35);padding:14px 16px;display:flex;gap:12px;' +
      'align-items:center;flex-wrap:wrap;font-family:Inter,system-ui,sans-serif;max-width:480px;margin:0 auto;}' +
      '#tca-pwa-banner img{width:44px;height:44px;border-radius:8px;flex-shrink:0;}' +
      '#tca-pwa-banner .tca-pwa-text{flex:1;min-width:180px;font-size:0.9rem;line-height:1.45;}' +
      '#tca-pwa-banner .tca-pwa-text strong{display:block;font-family:"Playfair Display",Georgia,serif;' +
      'font-weight:700;color:#C8971A;font-size:1rem;margin-bottom:2px;}' +
      '#tca-pwa-banner .tca-pwa-actions{display:flex;gap:8px;align-items:center;}' +
      '#tca-pwa-banner button{font:inherit;font-size:0.85rem;font-weight:600;cursor:pointer;border-radius:6px;padding:8px 14px;}' +
      '#tca-pwa-banner .tca-pwa-install{background:#C8971A;color:#0B1D35;border:none;}' +
      '#tca-pwa-banner .tca-pwa-dismiss{background:transparent;color:#F5EDE0;border:1px solid rgba(245,237,224,0.4);}' +
      '</style>' +
      '<img src="/icon-192.png" alt="">' +
      '<div class="tca-pwa-text">' + bodyHtml + '</div>' +
      '<div class="tca-pwa-actions">' + actionsHtml + '</div>';
    return el;
  }

  function removeBanner() {
    if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    banner = null;
  }

  function showInstallBanner() {
    if (banner) return;
    banner = buildBanner(
      '<strong>Texas CNA Academy</strong> Install the app for quick access from your home screen.',
      '<button type="button" class="tca-pwa-install">Install</button>' +
      '<button type="button" class="tca-pwa-dismiss">Not now</button>'
    );
    document.body.appendChild(banner);
    banner.querySelector('.tca-pwa-install').addEventListener('click', function () {
      if (!deferredPrompt) { removeBanner(); return; }
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(function () {
        deferredPrompt = null;
        removeBanner();
      });
    });
    banner.querySelector('.tca-pwa-dismiss').addEventListener('click', function () {
      rememberDismissed();
      removeBanner();
    });
  }

  function showIosBanner() {
    if (banner) return;
    banner = buildBanner(
      '<strong>Texas CNA Academy</strong> Add this app to your home screen: tap the Share button ' +
      '<span aria-hidden="true">&#x2191;</span> then choose <b>&ldquo;Add to Home Screen&rdquo;</b>.',
      '<button type="button" class="tca-pwa-dismiss">Got it</button>'
    );
    document.body.appendChild(banner);
    banner.querySelector('.tca-pwa-dismiss').addEventListener('click', function () {
      rememberDismissed();
      removeBanner();
    });
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showInstallBanner);
    } else {
      showInstallBanner();
    }
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    removeBanner();
  });

  /* iOS Safari never fires beforeinstallprompt — show manual instructions instead. */
  if (isIos()) {
    var showIos = function () { window.setTimeout(showIosBanner, 2500); };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showIos);
    } else {
      showIos();
    }
  }
})();
