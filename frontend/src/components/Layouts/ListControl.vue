<template>
    <ViewControls :key="doctype" ref="viewControls" v-model="listData" v-model:loadMore="loadMore"
        v-model:resizeColumn="triggerResize" v-model:updatedPageCount="updatedPageCount" :doctype="doctype"
        :filters="{}" :options="{allowedViews: ['list', 'group_by', 'kanban']}" />
</template>

<script setup>
import { defineProps } from 'vue'
import ViewControls from '@/components/ViewControls.vue'

const props = defineProps({
    listData: Object,
    loadMore: Function,
    triggerResize: Function,
    updatedPageCount: Function,
    doctype: String,
    filters: Object,
    options: Object
})
const { listData, loadMore, triggerResize, updatedPageCount, doctype } = props
console.log(listData,'listData')
</script>