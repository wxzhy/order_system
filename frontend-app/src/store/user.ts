import type { IUserInfoRes } from '@/api/types/login'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserInfo } from '@/api/login'

const defaultAvatar = '/static/images/default-avatar.png'

const initialState: IUserInfoRes = {
  id: -1,
  username: '',
  email: '',
  phone: '',
  user_type: 'customer',
  create_time: '',
  avatar: defaultAvatar,
}

export const useUserStore = defineStore(
  'user',
  () => {
    const userInfo = ref<IUserInfoRes>({ ...initialState })

    const setUserInfo = (val: IUserInfoRes) => {
      userInfo.value = {
        ...val,
        avatar: val.avatar || defaultAvatar,
      }
    }

    const setUserAvatar = (avatar: string) => {
      userInfo.value.avatar = avatar
    }

    const clearUserInfo = () => {
      userInfo.value = { ...initialState }
      uni.removeStorageSync('user')
    }

    const fetchUserInfo = async () => {
      const res = await getUserInfo()
      setUserInfo(res)
      return res
    }

    return {
      userInfo,
      setUserInfo,
      setUserAvatar,
      clearUserInfo,
      fetchUserInfo,
    }
  },
  {
    persist: true,
  },
)
