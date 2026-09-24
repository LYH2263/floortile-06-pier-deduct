<script setup>
defineProps({
  result: { type: Object, default: null },
})
</script>
<template>
  <div v-if="result" class="order-summary">
    <div class="hero">{{ result.order_count }} 片</div>
    <ul>
      <li>净用量 {{ result.raw_count }} 片，损耗 {{ result.waste_pct }}%</li>
      <li v-if="result.deduct_area_m2 > 0">毛面积 {{ result.gross_area_m2 }} m²，扣除柱墩 {{ result.deduct_area_m2 }} m²</li>
      <li>净面积 {{ result.area_m2 }} m²，单砖 {{ result.piece_m2 }} m²</li>
    </ul>
  </div>
</template>
