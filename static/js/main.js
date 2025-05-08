async function updateResults() {
    try {
        const response = await fetch('/get-images');
        if (!response.ok) {
            throw new Error('获取图片列表失败');
        }
        const data = await response.json();
        
        function updateTabContent(tabId, images) {
            const container = document.getElementById(tabId);
            if (images.length === 0) {
                container.innerHTML = `
                    <div class="text-center p-3">
                        <i class="bi bi-info-circle"></i>
                        <p class="mb-0">暂无图片</p>
                    </div>
                `;
            } else {
                container.innerHTML = '';
                images.forEach(img => {
                    container.appendChild(createImageElement(img));
                });
            }
        }
        
        updateTabContent('success', data.success);
        updateTabContent('failed', data.failed);
        updateTabContent('no-exif', data.no_exif);
    } catch (error) {
        console.error('更新结果失败:', error);
    }
}

function createImageElement(img) {
    const container = document.createElement('div');
    container.className = 'image-wrapper';
    container.style.position = 'relative';
    container.style.width = '150px';
    container.style.height = '150px';
    container.style.margin = '5px';
    container.style.borderRadius = '5px';
    container.style.overflow = 'hidden';
    container.style.backgroundColor = '#f8f9fa';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-spinner';
    loadingDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
    loadingDiv.style.position = 'absolute';
    loadingDiv.style.top = '50%';
    loadingDiv.style.left = '50%';
    loadingDiv.style.transform = 'translate(-50%, -50%)';
    container.appendChild(loadingDiv);

    const imgElement = document.createElement('img');
    imgElement.src = img.path;
    imgElement.className = 'preview-image';
    imgElement.title = img.name;
    imgElement.style.opacity = '1';
    imgElement.style.transition = 'opacity 0.3s ease';
    imgElement.style.width = '100%';
    imgElement.style.height = '100%';
    imgElement.style.objectFit = 'cover';

    function removeAllLoading() {
        const spinners = container.querySelectorAll('.loading-spinner');
        spinners.forEach(spinner => spinner.remove());
    }
    imgElement.onload = imgElement.onerror = removeAllLoading;  // 确保加载完成或失败时移除动画
    if (imgElement.complete) {
        removeAllLoading();
    }
    container.appendChild(imgElement);
    return container;
}

// 实时进度更新
socket.on('progress', (data) => {
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = `${data.progress}%`;
    progressBar.textContent = `${data.progress}%`;
});

// 字体大小自动按钮
autoFontSizeBtn.addEventListener('click', () => {
    fontSize.value = 0; // 设置为0表示自动
    fontSizeValue.textContent = '自动';
});

fontSize.addEventListener('input', (e) => {
    fontSizeValue.textContent = e.target.value == 0 ? '自动' : e.target.value;
});

const watermarkToggle = document.getElementById('watermarkToggle');
const watermarkPreview = document.getElementById('watermarkPreview');
const watermarkPosition = document.getElementById('watermarkPosition');

// 修复自动模式字体大小逻辑
function calculateFontSize(width, height) {
    return Math.max(Math.min(width, height) / 20, 12); // 根据分辨率动态计算字体大小
}

// 更新水印预览字体大小
function updateWatermarkPreviewFontSize() {
    const watermarkPreview = document.getElementById('watermarkPreview');
    const watermarkPosition = document.getElementById('watermarkPosition');
    const rect = watermarkPosition.getBoundingClientRect();
    const fontSize = calculateFontSize(rect.width, rect.height);
    watermarkPreview.style.fontSize = `${fontSize}px`;
}

// 初始化水印预览
function initializeWatermarkPreview() {
    const watermarkPreview = document.getElementById('watermarkPreview');
    watermarkPreview.style.display = 'block';
    updateWatermarkPreviewFontSize();
}

// 水印显示开关逻辑
watermarkToggle.addEventListener('change', (e) => {
    watermarkPreview.style.display = e.target.checked ? 'block' : 'none';
});

// 修复水印拖动逻辑
let isDragging = false;
let offsetX, offsetY;

watermarkPreview.addEventListener('mousedown', (e) => {
    isDragging = true;
    offsetX = e.offsetX;
    offsetY = e.offsetY;
    watermarkPreview.style.cursor = 'grabbing';
});

document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        const rect = watermarkPosition.getBoundingClientRect();
        let x = e.clientX - rect.left - offsetX;
        let y = e.clientY - rect.top - offsetY;

        // 限制水印在容器内移动
        x = Math.max(0, Math.min(x, rect.width - watermarkPreview.offsetWidth));
        y = Math.max(0, Math.min(y, rect.height - watermarkPreview.offsetHeight));

        watermarkPreview.style.left = `${x}px`;
        watermarkPreview.style.top = `${y}px`;
    }
});

document.addEventListener('mouseup', () => {
    if (isDragging) {
        isDragging = false;
        watermarkPreview.style.cursor = 'move';
    }
});

// 修复前端水印位置设置按钮的功能
const printPositionSelect = document.getElementById('printPosition');
printPositionSelect.addEventListener('change', (e) => {
    const selectedPosition = e.target.value;
    console.log(`水印位置设置为: ${selectedPosition}`);
    // 将选择的水印位置发送到后端
    const formData = new FormData();
    formData.append('print_position', selectedPosition);
    fetch('/update-watermark-position', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            console.log('水印位置更新成功');
        } else {
            console.error('水印位置更新失败');
        }
    }).catch(error => {
        console.error('发送水印位置时出错:', error);
    });
});

// 监听窗口大小变化，动态调整水印预览字体大小
window.addEventListener('resize', updateWatermarkPreviewFontSize);

// 初始化
initializeWatermarkPreview();
