import { useState, useCallback } from 'react';

interface NotificationConfig {
  title?: string;
  message: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}

interface NotificationState extends NotificationConfig {
  isOpen: boolean;
}

export const useNotification = () => {
  const [notification, setNotification] = useState<NotificationState>({
    isOpen: false,
    message: '',
    type: 'info',
    showCancel: true
  });

  const showNotification = useCallback((config: NotificationConfig) => {
    setNotification({
      isOpen: true,
      ...config
    });
  }, []);

  const hideNotification = useCallback(() => {
    setNotification(prev => ({
      ...prev,
      isOpen: false
    }));
  }, []);

  const confirm = useCallback((config: Omit<NotificationConfig, 'showCancel'>) => {
    return new Promise<boolean>((resolve) => {
      setNotification({
        isOpen: true,
        showCancel: true,
        ...config,
        onConfirm: () => {
          hideNotification();
          if (config.onConfirm) config.onConfirm();
          resolve(true);
        },
        onCancel: () => {
          hideNotification();
          if (config.onCancel) config.onCancel();
          resolve(false);
        }
      });
    });
  }, [hideNotification]);

  const alert = useCallback((config: Omit<NotificationConfig, 'showCancel' | 'onCancel'>) => {
    return new Promise<void>((resolve) => {
      setNotification({
        isOpen: true,
        showCancel: false,
        ...config,
        onConfirm: () => {
          hideNotification();
          if (config.onConfirm) config.onConfirm();
          resolve();
        }
      });
    });
  }, [hideNotification]);

  const handleConfirm = useCallback(() => {
    if (notification.onConfirm) {
      notification.onConfirm();
    }
    hideNotification();
  }, [notification, hideNotification]);

  const handleCancel = useCallback(() => {
    if (notification.onCancel) {
      notification.onCancel();
    }
    hideNotification();
  }, [notification, hideNotification]);

  return {
    notification: {
      ...notification,
      onConfirm: handleConfirm,
      onCancel: handleCancel
    },
    showNotification,
    hideNotification,
    confirm,
    alert
  };
};
