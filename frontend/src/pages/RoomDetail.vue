<script setup>
import { onMounted, ref } from 'vue'
import { deleteJSON, getJSON, postJSON } from '../api'

const props = defineProps({ id: String })
const room = ref(null)
const pLength = ref('')
const pWidth = ref('')
const err = ref('')

async function reload() {
  room.value = await getJSON(`/api/rooms/${props.id}`)
}
onMounted(reload)

async function addPillar() {
  err.value = ''
  try {
    await postJSON(`/api/rooms/${props.id}/pillars`, {
      length: Number(pLength.value),
      width: Number(pWidth.value),
    })
    pLength.value = ''
    pWidth.value = ''
    await reload()
  } catch (e) {
    err.value = e.message
  }
}

async function removePillar(p) {
  err.value = ''
  try {
    await deleteJSON(`/api/rooms/${props.id}/pillars/${p.id}`)
    await reload()
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
      <dt>柱墩扣除</dt><dd>{{ room.deduct_area_m2 }} m²</dd>
      <dt>净面积</dt><dd>{{ room.net_area_m2 }} m²</dd>
    </dl>
    <div v-if="room.net_area_m2 <= 0" class="alert">柱墩扣除已达到或超过毛面积，测算将失败，请调整柱墩。</div>

    <h2>柱墩块</h2>
    <table v-if="room.pillars?.length" class="tbl">
      <thead><tr><th>长 (m)</th><th>宽 (m)</th><th>面积 (m²)</th><th></th></tr></thead>
      <tbody>
        <tr v-for="p in room.pillars" :key="p.id">
          <td>{{ p.length }}</td>
          <td>{{ p.width }}</td>
          <td>{{ (p.length * p.width).toFixed(3) }}</td>
          <td><button @click="removePillar(p)">删除</button></td>
        </tr>
      </tbody>
    </table>
    <p v-else>暂无柱墩，按毛面积测算。</p>
    <form @submit.prevent="addPillar">
      <label>长 (m) <input v-model="pLength" type="number" step="any" min="0" required></label>
      <label>宽 (m) <input v-model="pWidth" type="number" step="any" min="0" required></label>
      <button type="submit">添加柱墩</button>
    </form>
    <p v-if="err" class="alert">{{ err }}</p>

    <router-link to="/bench">去测算</router-link>
  </div>
</template>
