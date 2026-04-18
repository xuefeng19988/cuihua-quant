<template>
  <div v-if="!item.hidden">
    <!-- Single Item -->
    <template v-if="hasOneShowingChild(item.children, item) && (!onlyOneChild.children || onlyOneChild.noShowingChildren)">
      <el-menu-item :index="resolvePath(onlyOneChild.path)">
        <i :class="onlyOneChild.meta.icon || item.meta.icon"></i>
        <span slot="title">{{ onlyOneChild.meta.title }}</span>
      </el-menu-item>
    </template>

    <!-- Sub Menu -->
    <el-submenu v-else :index="resolvePath(item.path)">
      <template slot="title">
        <i :class="item.meta.icon"></i>
        <span slot="title">{{ item.meta.title }}</span>
      </template>
      <sidebar-item v-for="child in item.children" :key="child.path" :item="child" :base-path="resolvePath(child.path)" />
    </el-submenu>
  </div>
</template>

<script>
export default {
  name: 'SidebarItem',
  props: { item: { type: Object, required: true }, basePath: { type: String, default: '' } },
  data() { return { onlyOneChild: null } },
  methods: {
    hasOneShowingChild(children = [], parent) {
      const showingChildren = children.filter(item => !item.hidden)
      if (showingChildren.length === 1) {
        this.onlyOneChild = showingChildren[0]
        return true
      }
      if (showingChildren.length === 0) {
        this.onlyOneChild = { ...parent, path: '', noShowingChildren: true }
        return true
      }
      return false
    },
    resolvePath(routePath) {
      if (this.basePath.endsWith('/')) return this.basePath + routePath
      return this.basePath + '/' + routePath
    }
  }
}
</script>
