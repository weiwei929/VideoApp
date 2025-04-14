/**
 * PikPak Player 增强脚本
 */

class PikPakPlayer {
    constructor(videoElement) {
        this.videoElement = videoElement;
        this.setupEvents();
    }
    
    setupEvents() {
        // 监听错误事件
        this.videoElement.addEventListener('error', (e) => {
            console.error('视频播放错误:', e);
            this.handleError(e);
        });
        
        // 监听缓冲事件
        this.videoElement.addEventListener('waiting', () => {
            console.log('视频缓冲中...');
        });
        
        // 监听播放事件
        this.videoElement.addEventListener('playing', () => {
            console.log('视频开始播放');
        });
    }
    
    handleError(error) {
        // 尝试恢复播放
        setTimeout(() => {
            console.log('尝试恢复播放...');
            this.videoElement.load();
            this.videoElement.play().catch(e => {
                console.error('恢复播放失败:', e);
            });
        }, 3000);
    }
}

// 导出类供其他模块使用
window.PikPakPlayer = PikPakPlayer;
