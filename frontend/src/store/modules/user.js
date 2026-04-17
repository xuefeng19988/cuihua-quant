import Cookies from 'js-cookie'

const state = {
  token: Cookies.get('token') || '',
  name: '',
  avatar: ''
}

const mutations = {
  SET_TOKEN: (state, token) => { state.token = token },
  SET_NAME: (state, name) => { state.name = name },
  SET_AVATAR: (state, avatar) => { state.avatar = avatar }
}

const actions = {
  login({ commit }, userInfo) {
    return new Promise((resolve, reject) => {
      // Login via Flask backend
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userInfo)
      })
      .then(res => res.json())
      .then(data => {
        if (data.code === 200) {
          commit('SET_TOKEN', data.token)
          Cookies.set('token', data.token)
          resolve()
        } else {
          reject(new Error(data.message))
        }
      })
      .catch(reject)
    })
  },
  getInfo({ commit }) {
    return new Promise((resolve) => {
      fetch('/api/auth/info')
        .then(res => res.json())
        .then(data => {
          if (data.code === 200) {
            commit('SET_NAME', data.name || '管理员')
            commit('SET_AVATAR', data.avatar || '🦜')
            resolve(data)
          }
        })
        .catch(() => resolve({}))
    })
  },
  logout({ commit }) {
    return new Promise((resolve) => {
      fetch('/api/auth/logout', { method: 'POST' })
        .then(() => {
          commit('SET_TOKEN', '')
          Cookies.remove('token')
          resolve()
        })
        .catch(() => {
          commit('SET_TOKEN', '')
          Cookies.remove('token')
          resolve()
        })
    })
  }
}

export default { namespaced: true, state, mutations, actions }
