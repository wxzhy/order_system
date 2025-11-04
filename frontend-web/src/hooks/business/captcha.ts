import { computed } from 'vue';
import { useCountDown, useLoading } from '@sa/hooks';
import { REG_EMAIL } from '@/constants/reg';
import { $t } from '@/locales';
import { EmailCodeScene, fetchSendEmailCode } from '@/service/api';

export function useEmailCaptcha(scene: EmailCodeScene) {
  const { loading, startLoading, endLoading } = useLoading();
  const { count, start, stop, isCounting } = useCountDown(60);

  const label = computed(() => {
    if (loading.value) {
      return '';
    }

    if (isCounting.value) {
      return $t('page.login.codeLogin.reGetCode', { time: count.value });
    }

    return $t('page.login.codeLogin.getCode');
  });

  function isEmailValid(email: string) {
    const value = email.trim();

    if (value === '') {
      window.$message?.error?.($t('form.email.required'));

      return false;
    }

    if (!REG_EMAIL.test(value)) {
      window.$message?.error?.($t('form.email.invalid'));

      return false;
    }

    return true;
  }

  async function getCaptcha(email: string) {
    if (!isEmailValid(email) || loading.value) {
      return;
    }

    startLoading();

    try {
      await fetchSendEmailCode(email, scene);
      window.$message?.success?.($t('page.login.codeLogin.sendCodeSuccess'));
      start();
    } finally {
      endLoading();
    }
  }

  return {
    label,
    isCounting,
    loading,
    getCaptcha,
    stop
  };
}
