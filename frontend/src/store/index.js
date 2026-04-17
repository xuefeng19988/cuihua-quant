import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import settings from './modules/settings'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: { user, settings },
  getters: {
    sidebar: state => state.settings.sidebar,
    token: state => state.user.token,
    name: state => state.user.name
  }
})
