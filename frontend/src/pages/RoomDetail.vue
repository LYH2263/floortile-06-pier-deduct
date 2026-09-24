<script setup>
import { onMounted, ref } from 'vue'
import { delJSON, getJSON, postJSON } from '../api'
const props = defineProps({ id: String })
const room = ref(null)
const err = ref('')
const form = ref({ name: '', length: '', width: '' })

async function load() { room.value = await getJSON(`/api/rooms/${props.id}`) }
onMounted(load)

async function addPier() {
  err.value = ''
  try {
    await postJSON(`/api/rooms/${props.id}/piers`, {
      name: form.value.name,
      length: Number(form.value.length),
      width: Number(form.value.width),
    })
    form.value = { name: '', length: '', width: '' }
    await load()
  } catch (e) {
    err.value = e.message
  }
}

async function removePier(p) {
  err.value = ''
  try {
    await delJSON(`/api/rooms/${props.id}/piers/${p.id}`)
    await load()
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page" v-if="room">
    <h1>{{ room.name }}</h1>
    <div v-if="room.data_quality === 'dirty'" class="alert">该房间尺寸异常：{{ room.note }}</div>
    <dl>
      <dt>长度</dt><dd>{{ room.length }} m</dd>
      <dt>宽度</dt><dd>{{ room.width }} m</dd>
      <dt>毛面积</dt><dd>{{ room.gross_area_m2 }} m²</dd>
      <dt>柱墩扣除</dt><dd>{{ room.deduct_m2 }} m²</dd>
      <dt>净面积</dt><dd><strong>{{ room.net_area_m2 }} m²</strong></dd>
    </dl>

    <h2>柱墩</h2>
    <table v-if="room.piers?.length" class="tbl">
      <thead><tr><th>名称</th><th>长×宽</th><th>面积</th><th></th></tr></thead>
      <tbody>
        <tr v-for="p in room.piers" :key="p.id">
          <td>{{ p.name || '—' }}</td>
          <td>{{ p.length }} × {{ p.width }} m</td>
          <td>{{ (p.length * p.width).toFixed(2) }} m²</td>
          <td><button @click="removePier(p)">删除</button></td>
        </tr>
      </tbody>
    </table>
    <p v-else>暂无柱墩，测算按毛面积。</p>
    <form @submit.prevent="addPier">
      <label>名称 <input v-model="form.name" placeholder="如 承重柱" /></label>
      <label>长(m) <input v-model="form.length" type="number" step="any" required /></label>
      <label>宽(m) <input v-model="form.width" type="number" step="any" required /></label>
      <button type="submit">添加柱墩</button>
    </form>
    <p v-if="err" class="alert">{{ err }}</p>
    <router-link to="/bench">去测算</router-link>
  </div>
</template>
