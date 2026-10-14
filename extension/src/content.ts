// This script runs in the context of the webpage
// It listens for messages from the side panel

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.action === 'extractText') {
    try {
      // 1. Clone the body so we don't accidentally modify the actual webpage
      const clonedBody = document.body.cloneNode(true) as HTMLElement;

      // 2. Remove noisy elements that we don't want to analyze
      const elementsToRemove = clonedBody.querySelectorAll(
        'script, style, noscript, nav, footer, header, iframe, img, svg, video, audio, canvas, time, form'
      );
      elementsToRemove.forEach((el) => el.remove());

      // 3. Extract the visible text
      const extractedText = clonedBody.innerText;

      // Clean up extra whitespace and empty lines
      const cleanText = extractedText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .join('\n');

      sendResponse({ success: true, text: cleanText });
    } catch (error) {
      sendResponse({ success: false, error: (error as Error).message });
    }
  } else if (request.action === 'highlightText') {
    try {
      const target = (request.text || '').trim();
      if (!target) {
        sendResponse({ success: false, error: 'No text to highlight' });
        return true;
      }

      // Remove previous highlights
      const existing = document.querySelectorAll('.smartconsent-highlight');
      existing.forEach((el) => {
        const parent = el.parentNode;
        if (parent) {
          parent.replaceChild(document.createTextNode(el.textContent || ''), el);
          parent.normalize();
        }
      });

      // Simple keyword / phrase search in document body
      const searchPhrase = target.length > 60 ? target.slice(0, 60) : target;
      
      const treeWalker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: (node) => {
            const parent = node.parentElement;
            if (!parent || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(parent.tagName)) {
              return NodeFilter.FILTER_REJECT;
            }
            return node.nodeValue && node.nodeValue.toLowerCase().includes(searchPhrase.toLowerCase())
              ? NodeFilter.FILTER_ACCEPT
              : NodeFilter.FILTER_SKIP;
          }
        }
      );

      const targetNode = treeWalker.nextNode();
      if (targetNode && targetNode.parentElement) {
        const text = targetNode.nodeValue || '';
        const idx = text.toLowerCase().indexOf(searchPhrase.toLowerCase());
        if (idx !== -1) {
          const span = document.createElement('mark');
          span.className = 'smartconsent-highlight';
          span.style.backgroundColor = '#fef08a';
          span.style.color = '#854d0e';
          span.style.padding = '2px 4px';
          span.style.borderRadius = '3px';
          span.style.boxShadow = '0 0 10px rgba(234, 179, 8, 0.8)';
          span.style.fontWeight = 'bold';
          span.style.transition = 'all 0.3s ease';

          const matchText = text.substring(idx, idx + searchPhrase.length);
          const afterText = text.substring(idx + searchPhrase.length);
          const beforeText = text.substring(0, idx);

          const parent = targetNode.parentElement;
          span.textContent = matchText;

          const fragment = document.createDocumentFragment();
          if (beforeText) fragment.appendChild(document.createTextNode(beforeText));
          fragment.appendChild(span);
          if (afterText) fragment.appendChild(document.createTextNode(afterText));

          parent.replaceChild(fragment, targetNode);
          span.scrollIntoView({ behavior: 'smooth', block: 'center' });

          sendResponse({ success: true, found: true });
          return true;
        }
      }

      sendResponse({ success: true, found: false });
    } catch (e) {
      sendResponse({ success: false, error: (e as Error).message });
    }
  }

  return true;
});

