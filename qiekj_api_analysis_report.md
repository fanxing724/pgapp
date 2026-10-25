# 切客纪 (qiekj) 官方 APK API 接口完整分析报告

## 基本信息

| 项目 | 值 |
|------|-----|
| **应用包名** | `com.qiekj.user` |
| **版本** | v1.144.0 (294) |
| **APK SHA-256** | `3ca981ee50b982ccf15cdd899e0ee34f15c195a2eefb5764e3ce95e40346b5d8` |
| **分析日期** | 2026-10-25 |
| **API 基础 URL** | `https://userapi.qiekj.com/` (HOST_URL) |
| **本地生活 URL** | BuildConfig.LOCAL_LIFE_HOST (StarsApi) |
| **商城 URL** | BuildConfig.MALL_HOST_URL (QeService) |
| **YApi Mock** | `http://yapi.qiekj.com/mock/11/` |

> ✅ **端点验证说明**：本报告中签到/广告/任务等关键接口的 URL 路径已通过 apktool 反编译的 `ApiService.smali` 中 Retrofit `@POST/@GET` 注解逐一验证（共提取 300 个真实端点），不再是推测。完整清单见 [ApiService_真实端点清单.md](ApiService_真实端点清单.md)。标注"推断路径"的章节仍为早期推测结果，仅供参考。

---

## 一、API 服务架构概览

### 1.1 Retrofit 服务实例

| 服务名称 | 接口类 | Base URL | 用途 |
|---------|--------|----------|------|
| `apiService` | `ApiService` | `HOST_URL` | 主业务 API |
| `userService` | `ApiService` | `HOST_URL` | 用户相关 API |
| `starsService` | `StarsApi` | `LOCAL_LIFE_HOST` | 本地生活/社区 API |
| `qeService` | `ApiService` | `MALL_HOST_URL` | 商城 API |
| `uselessService` | `DisApiService` | `HOST_URL` | 分发/排名 API |
| `uploadService` | `ApiService` | `HOST_URL` | 文件上传 API |
| `starsUploadService` | `StarsApi` | `LOCAL_LIFE_HOST` | 社区文件上传 |
| `yApiService` | `ApiService` | YApi Mock | 测试/Mock 环境 |

### 1.2 网络拦截器

| 拦截器 | 功能 |
|--------|------|
| `HeadInterceptor` | 添加请求头（token, version, channel, deviceId, sign等） |
| `SignInterceptor` | 请求签名验证 |
| `BusinessErrorReportInterceptor` | 业务错误上报 |

### 1.3 请求签名算法

```
sign = SHA-256("appSecret={secret}&channel=android_app&timestamp={ts}&token={token}&version={version}&{path}")
```

特殊路径（`/goods/shower/unlock`, `/goods/water/unlock`, `/trade/create`）需要额外的 `orderRiskSign`：
```
orderRiskSign = SHA-256("appSecret={LOCATION_SECRET}&categoryCode={code}&channel=android_app&imei={imei}&lat={lat}&lng={lng}&timestamp={ts}&token={token}&version={version}&{path}")
```

---

## 二、API 接口完整清单

### 2.1 ApiService (301 个方法) - 主业务接口

#### 📱 用户认证与账户管理 (28个)

| 方法名 | 推断路径 | 功能描述 | GitHub对应 |
|--------|---------|---------|-----------|
| `login` | `user/reg` | 用户登录/注册 | ✅ `user/reg` |
| `sendCode` | `common/sms/sendCode` | 发送短信验证码 | ✅ `common/sms/sendCode` |
| `smsCode` | `common/sms/verify` | 验证短信码 | - |
| `checkLogin` | `user/checkLogin` | 检查登录状态 | - |
| `userInfo` | `user/info` | 获取用户信息 | - |
| `userHome` | `user/home` | 用户主页数据 | - |
| `updateHeadImg` | `user/updateHeadImg` | 更新头像 | - |
| `infoEdit` | `user/info/edit` | 编辑用户信息 | - |
| `replacePhone` | `user/replacePhone` | 更换绑定手机 | - |
| `encryptPhone` | `user/encryptPhone` | 加密手机号 | - |
| `aliLogin` | `user/ali/login` | 支付宝登录 | - |
| `aliBind` | `user/ali/bind` | 绑定支付宝 | - |
| `wechatLogin` | `user/wechat/login` | 微信登录 | - |
| `wechatBind` | `user/wechat/bind` | 绑定微信 | - |
| `wechatJustBind` | `user/wechat/justBind` | 仅绑定微信 | - |
| `wechatUnbind` | `user/wechat/unbind` | 解绑微信 | - |
| `taobaoBind` | `user/taobao/bind` | 绑定淘宝 | - |
| `taobaoCheckBind` | `user/taobao/checkBind` | 检查淘宝绑定 | - |
| `zfbBind` | `user/zfb/bind` | 绑定支付宝(旧) | - |
| `zfbUnbind` | `user/zfb/unbind` | 解绑支付宝 | - |
| `accBindInfo` | `user/acc/bindInfo` | 账户绑定信息 | - |
| `agentBind` | `user/agent/bind` | 代理商绑定 | - |
| `passphrase` | `user/passphrase` | 密码/口令验证 | - |
| `verify` | `user/verify` | 身份验证 | - |
| `isNeedRealName` | `user/isNeedRealName` | 是否需要实名 | - |
| `checkUserIsRisk` | `userIntegral/checkUserIsRisk` | 检查用户风险 | ✅ `userIntegral/checkUserIsRisk` |
| `checkUserPortrait` | `user/checkPortrait` | 检查用户画像 | - |
| `getEncodeUserId` | `user/getEncodeUserId` | 获取加密用户ID | - |

#### 💰 余额与支付 (25个)

| 方法名 | 推断路径 | 功能描述 | GitHub对应 |
|--------|---------|---------|-----------|
| `queryBalance` / `userBalance` | `user/balance` | 查询余额 | ✅ `user/balance` |
| `getUserBalance` | `user/getBalance` | 获取用户余额 | - |
| `withBalance` | `user/withBalance` | 提现到余额 | - |
| `payPreBalance` | `pay/preBalance` | 预扣余额 | - |
| `availablePayType` | `pay/availableType` | 可用支付方式 | - |
| `prePayChannel` | `payChannelRoute/pre` | 预付渠道 | - |
| `afterPayChannel` | `payChannelRoute/after` | 后付渠道 | - |
| `addAfterPayChannel` | `payChannelRoute/addUserAfterPayChannel` | 添加后付渠道 | ✅ `payChannelRoute/addUserAfterPayChannel` |
| `againPayChannel` | `payChannelRoute/again` | 重新支付渠道 | - |
| `walletPay` | `pay/wallet` | 钱包支付 | - |
| `alipaySign` | `pay/alipay/sign` | 支付宝签约 | - |
| `unionPaySign` | `pay/union/sign` | 银联签约 | - |
| `jumpAlipay` | `pay/jumpAlipay` | 跳转支付宝 | - |
| `perPay` | `pay/perPay` | 个人支付 | - |
| `createVirtualOrder` | `order/virtual/create` | 创建虚拟订单 | - |
| `virtualOrderCreate` | `order/virtual/createV2` | 虚拟订单创建V2 | - |
| `coinRefund` | `coin/refund` | 代币退款 | - |
| `coinRefundDetails` | `coin/refund/details` | 退款详情 | - |
| `coinRefundRecords` | `coin/refund/records` | 退款记录 | - |
| `tokenCoinRefundCancel` | `coin/refund/cancel` | 取消代币退款 | - |
| `tokenCoinRefundPlatformApply` | `coin/refund/platformApply` | 平台申请退款 | - |
| `queryCashierMarketing` | `cashier/marketing/query` | 收银台营销查询 | - |
| `sdkResult` | `pay/sdk/result` | SDK支付结果 | - |
| `hzEncrypt` | `pay/hz/encrypt` | 杭州加密支付 | - |
| `icbcQueryGrant` | `pay/icbc/queryGrant` | 工行授权查询 | - |

#### 🛒 订单管理 (32个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `orderCreate` | `order/create` | 创建订单 |
| `orderPreCreate` | `order/preCreate` | 预创建订单 |
| `orderDetails` | `order/detail` | 订单详情 |
| `orderPreDetail` | `order/preDetail` | 预订单详情 |
| `orderMy` | `order/my` | 我的订单列表 |
| `orderCount` | `order/count` | 订单数量统计 |
| `orderCancel` | `order/cancel` | 取消订单 |
| `orderHidden` | `order/hidden` | 隐藏订单 |
| `orderStart` | `order/start` | 开始订单 |
| `orderSync` | `order/sync` | 订单同步 |
| `orderPayStatus` | `order/payStatus` | 支付状态查询 |
| `orderAppointCancel` | `order/appoint/cancel` | 预约订单取消 |
| `orderReserveMy` | `order/reserve/my` | 我的预订订单 |
| `tradePreviewV2` | `trade/preview/v2` | 交易预览V2 |
| `confirmRenewal` | `order/renewal/confirm` | 确认续费 |
| `distributorOrderList` | `distributor/order/list` | 分销商订单列表 |
| `distributorOrderDetail` | `distributor/order/detail` | 分销商订单详情 |
| `distributorOrderDelete` | `distributor/order/delete` | 删除分销商订单 |
| `attachList` | `attach/list` | 附加服务列表 |
| `attachListV2` | `attach/list/v2` | 附加服务列表V2 |
| `attachOrderDetails` | `attach/order/details` | 附加订单详情 |
| `attachOrderCancel` | `attach/order/cancel` | 取消附加订单 |
| `attachOrderHidden` | `attach/order/hidden` | 隐藏附加订单 |
| `latestUsed` | `goods/latestUsed` | 最近使用设备 |
| `goodsLastOrder` | `goods/lastOrder` | 商品最后订单 |
| `suishoubuCreate` | `order/suishoubu/create` | 随手布创建订单 |
| `failureUp` | `order/failure/up` | 故障上报 |
| `feedback` | `order/feedback` | 订单反馈 |
| `satisfactionSurveyDetail` | `survey/satisfaction/detail` | 满意度调查详情 |
| `cmd` | `device/cmd` | 设备指令 |
| `downgrade` | `order/downgrade` | 订单降级 |
| `downgradeCheck` | `order/downgrade/check` | 降级检查 |

#### 🔌 设备控制与解锁 (22个)

| 方法名 | 推断路径 | 功能描述 | GitHub对应 |
|--------|---------|---------|-----------|
| `showerUnlock` | `goods/shower/unlock` | 淋浴设备解锁 | - |
| `bleShowerUnlock` | `goods/shower/ble/unlock` | 蓝牙淋浴解锁 | - |
| `waterEnd` | `goods/water/end` | 用水结束 | - |
| `waterSync` | `goods/water/sync` | 用水同步 | ✅ `goods/water/sync` |
| `waterLadder` | `goods/water/ladder` | 用水阶梯计费 | - |
| `waterQuotaActive` | `goods/water/quota/active` | 用水配额激活 | - |
| `waterVipFlag` | `goods/water/vipFlag` | 用水VIP标识 | - |
| `bleWaterUnlock` | `goods/water/ble/unlock` | 蓝牙用水解锁 | - |
| `goodsWaterUnlock` | `goods/water/unlock` | 用水解锁 | ✅ `goods/water/unlock` |
| `deviceCheck` | `device/check` | 设备检查 | - |
| `deviceFault` | `device/fault` | 设备故障上报 | - |
| `deviceStartStatus` | `device/start/status` | 设备启动状态 | - |
| `checkMachineCanUse` | `device/canUse` | 检查设备可用性 | - |
| `machineModelList` | `device/model/list` | 设备型号列表 | - |
| `shopMachineModel` | `shop/device/model` | 店铺设备型号 | - |
| `shopTypeMachines` | `shop/type/machines` | 店铺类型设备 | - |
| `shopPointMachines` | `shop/point/machines` | 点位设备列表 | - |
| `resetShowerPwd` | `device/shower/resetPwd` | 重置淋浴密码 | - |
| `saveShowerPwd` | `device/shower/savePwd` | 保存淋浴密码 | - |
| `showerDetail` | `device/shower/detail` | 淋浴设备详情 | - |
| `showerList` | `device/shower/list` | 淋浴设备列表 | - |
| `showerSync` | `device/shower/sync` | 淋浴设备同步 | - |

#### 🏪 商铺与门店 (20个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `nearbyShop` | `shop/nearby` | 附近商铺 |
| `nearbyShopForShower` | `shop/nearby/shower` | 附近淋浴商铺 |
| `nearByList` | `shop/nearby/list` | 附近列表 |
| `shopOutline` | `shop/outline` | 商铺概况 |
| `shopOutlineV2` | `shop/outline/v2` | 商铺概况V2 |
| `shopDetail` / `lifeShopDetail` | `shop/detail` | 商铺详情 |
| `shopPoint` | `shop/point` | 商铺点位 |
| `shopTag` | `shop/tag` | 商铺标签 |
| `shopVip` | `shop/vip` | 商铺VIP |
| `popShop` | `shop/pop` | 弹窗商铺 |
| `queryAreaList` | `area/list` | 区域列表 |
| `queryAreaTree` | `area/tree` | 区域树形结构 |
| `localLifeTab` | `locallife/tab` | 本地生活Tab |
| `localLifeCategory` | `locallife/category` | 本地生活分类 |
| `localLifeGoodsList` | `locallife/goods/list` | 本地生活商品 |
| `sectionRender` | `section/render` | 板块渲染 |
| `bottomBar` | `config/bottomBar` | 底部导航栏配置 |
| `homeApp` | `config/home/app` | 首页App配置 |
| `horseRaceLamp` | `config/horseRaceLamp` | 跑马灯配置 |
| `cacheUrlData` | `config/cache/url` | 缓存URL数据 |

#### 🎫 优惠券与营销 (28个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `newCoupon` | `coupon/new` | 新优惠券 |
| `couponDetail` | `coupon/detail` | 优惠券详情 |
| `couponBloat` | `coupon/bloat` | 优惠券膨胀 |
| `couponSchedule` | `coupon/schedule` | 优惠券计划 |
| `availableCount` | `coupon/available/count` | 可用券数量 |
| `usableCouponList` | `coupon/usable/list` | 可用券列表 |
| `invalidCouponList` | `coupon/invalid/list` | 无效券列表 |
| `afterVoucherCoupon` | `voucher/after/coupon` | 券后优惠 |
| `afterDiscount` | `voucher/after/discount` | 券后折扣 |
| `valueCouponPackCreate` | `coupon/pack/create` | 创建券包 |
| `queryCouponByVip` | `coupon/vip/query` | VIP优惠券查询 |
| `vipRewardVoucher` | `vip/reward/voucher` | VIP奖励券 |
| `voucherScene` | `voucher/scene` | 券场景 |
| `queryFlashSaleVoucherClaimResult` | `flashsale/voucher/result` | 限时抢券结果 |
| `marketingScheduleReward` | `marketing/schedule/reward` | 营销计划奖励 |
| `queryMarketingSchedule` | `marketing/schedule/query` | 营销计划查询 |
| `shareMarketing` | `marketing/share` | 分享营销 |
| `mallRebateConfig` | `mall/rebate/config` | 商城返利配置 |
| `mallRebateOrderPage` | `mall/rebate/order/page` | 返利订单分页 |
| `mallRedirect` | `mall/redirect` | 商城重定向 |
| `tapRedPacketExpose` | `redpacket/expose` | 红包曝光 |
| `tapRedPacketReceive` | `redpacket/receive` | 红包领取 |
| `checkRedEnvelope` | `redpacket/check` | 检查红包 |
| `receiveRedEnvelope` | `redpacket/receiveV2` | 领取红包V2 |
| `lotteryConfig` | `lottery/config` | 抽奖配置 |
| `luckyBagIntegral` | `luckybag/integral` | 福袋积分 |
| `timedBenefit` | `benefit/timed` | 定时福利 |
| `timedBenefitReward` | `benefit/timed/reward` | 定时福利奖励 |

#### ⭐ 积分与任务 (30个) — ✅ 真实路径（smali 验证）

| 方法名 | 真实路径 | 功能描述 |
|--------|---------|---------|
| `userIntegralRule` | `userIntegral/limitRule` | 积分规则 |
| `integralTaskList` | `task/list` | 积分任务列表 |
| `integralCaptcha` | `integralCaptcha/isCaptcha` | 积分验证码 |
| `integralDailStatistics` | `integralRecord/integralDailStatistics` | 每日积分统计 |
| `integralLayer` | `userIntegral/userIntegralLayer` | 积分层级 |
| `integralGoodsPage` | `integralGoods/queryIntegralGoodsPage` | 积分商品分页 |
| `integralUmpConfig` | `integralUmp/config` (GET) | 积分UMP配置 |
| `consumeIntegralRate` | `integralUmp/consumeIntegralRateForDay` (GET) | 积分消耗比率 |
| `rewardIntegral` | `integralUmp/rewardIntegral` | 奖励积分 |
| `applyTask` | `markActivity/doApplyTask` | 申请任务 |
| `applyTaskPackage` | `taskPackage/applyTask` (GET) | 申请任务包 |
| `queryTask` | `task/queryByType` | 查询任务 |
| `queryTaskAccount` | `markActivity/queryMarkTaskAccount` | 任务账户查询 |
| `queryTaskByTime` | `markActivity/queryMarkTaskByStartTime` | 按时间查任务 |
| `queryTaskPackage` | `taskPackage/queryApplyTask` (GET) | 查询任务包 |
| `queryThirdTask` | `task/queryThirdPartyJumpLink` | 第三方任务查询 |
| `queryPushTask` | `task/queryPushTask` | 推送任务查询 |
| `taskApplyCost` | `markActivity/markTaskApplyCost` (GET) | 任务申请成本 |
| `taskBubble` | `task/taskBubble` | 任务气泡 |
| `taskCompleted` | `task/completed` | 任务完成 |
| `taskReward` | `markActivity/markTaskReward` | 任务奖励 |
| `taskPackageReward` | `taskPackage/applyReward` | 任务包奖励 |
| `getTaskReward` | `task/getTaskReward` | 获取任务奖励 |
| `doMarkTask` | `markActivity/doMarkTask` | 标记任务 |
| `guideTaskList` | `taskPackage/drainageTaskList` | 引导任务列表 |
| `pageOnlineEarnTask` | `onlineEarn/pageOnlineEarnTask` | 在线赚任务分页 |
| `earnBenefitsTask` | `task/earnBenefitsTask` | 赚取福利任务 |
| `ladderTask` | `ladderTask/ladderTaskForDay` (GET) | 阶梯任务 |
| `applyLadderReward` | `ladderTask/applyLadderReward` | 申请阶梯奖励 |
| `queryAsyncReward` | `task/queryAsyncReward` | 异步奖励查询 |

#### 👑 VIP 会员 (18个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `vipList` | `vip/list` | VIP列表 |
| `vipCreate` | `vip/create` | 创建VIP订单 |
| `vipOrderDetail` | `vip/order/detail` | VIP订单详情 |
| `vipRenew` | `vip/renew` | VIP续费 |
| `vipRenewalDialog` | `vip/renewal/dialog` | 续费弹窗 |
| `vipQueryDiscount` | `vip/discount/query` | VIP折扣查询 |
| `vipReadDiscount` | `vip/discount/read` | 读取VIP折扣 |
| `vipSignDetail` | `vip/sign/detail` | VIP签约详情 |
| `vipSignUrl` | `vip/sign/url` | VIP签约URL |
| `signUrl` | `sign/url` | 签约URL |
| `signUrlPinpoint` | `sign/url/pinpoint` | 精确定位签约URL |
| `penguinVipDetail` | `vip/penguin/detail` | 企鹅VIP详情 |
| `penguinVipStatus` | `vip/penguin/status` | 企鹅VIP状态 |
| `pgVipConfig` | `vip/penguin/config` | 企鹅VIP配置 |
| `userVipInfo` | `user/vip/info` | 用户VIP信息 |
| `reportPenguinVisit` | `vip/penguin/report` | 上报企鹅访问 |
| `weeklyList` | `vip/weekly/list` | 周卡列表 |
| `weeklyConDay` | `vip/weekly/conDay` | 周卡连续天数 |

#### 📦 商品与SKU (15个)

| 方法名 | 推断路径 | 功能描述 | GitHub对应 |
|--------|---------|---------|-----------|
| `goodsDetails` | `goods/normal/details` | 商品详情 | ✅ `goods/normal/details` |
| `skus` | `goods/normal/skus` | SKU列表 | ✅ `goods/normal/skus` |
| `goodsFictitious` | `goods/fictitious` | 虚拟商品 | - |
| `itemList` | `goods/item/list` | 商品列表 | - |
| `goodsCategoryStatistics` | `goods/category/stats` | 商品分类统计 | - |
| `canUseList` | `goods/canUse/list` | 可用商品列表 | - |
| `selectTime` | `goods/select/time` | 选择时间 | - |
| `reserveFunctionList` | `goods/reserve/function` | 预约功能列表 | - |
| `reserveAdd` | `goods/reserve/add` | 添加预约 | - |
| `getTakeawayGoods` | `goods/takeaway` | 外卖商品 | - |
| `searchRecommend` | `search/recommend` | 搜索推荐 | - |
| `searchResult` | `search/result` | 搜索结果 | - |
| `dyDetail` | `goods/dy/detail` | 抖音商品详情 | - |
| `getXianyuJumpLink` | `goods/xianyu/jump` | 闲鱼跳转链接 | - |
| `xianyuAdTrack` | `ad/xianyu/track` | 闲鱼广告追踪 | - |

#### 📍 定位与地址 (10个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `isCheckLocation` | `orderRisk/isCheckLocation` | 是否检查位置 | ✅ |
| `queryUserAddress` | `address/user/query` | 查询用户地址 |
| `queryUserAddressList` | `address/user/list` | 用户地址列表 |
| `saveUserAddress` | `address/user/save` | 保存用户地址 |
| `editUserAddress` | `address/user/edit` | 编辑用户地址 |
| `removeUserAddress` | `address/user/remove` | 删除用户地址 |
| `modifyDefaultAddress` | `address/default/modify` | 修改默认地址 |
| `isShowTableBoard` | `config/tableBoard/show` | 是否显示看板 |
| `shouldPopup` | `config/popup/should` | 是否弹窗 |
| `platformCheck` | `platform/check` | 平台检查 |

#### 📢 消息与通知 (10个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `messageList` | `message/list` | 消息列表 |
| `messageCount` | `message/count` | 消息数量 |
| `messageRead` | `message/read` | 标记已读 |
| `msgSync` | `message/sync` | 消息同步 |
| `homeMsgList` | `message/home/list` | 首页消息列表 |
| `getuiBindUser` | `push/getui/bind` | 个推绑定用户 |
| `freqForAccount` | `push/freq/account` | 推送频率设置 |
| `queryShielding` | `message/shielding/query` | 屏蔽消息查询 |
| `serectReport` | `report/secret` | 密报 |
| `newcomerContext` | `user/newcomer/context` | 新人上下文 |

#### 📊 签到与活跃 (12个) — ✅ 真实路径（smali 验证）

| 方法名 | 真实路径 | 功能描述 |
|--------|---------|---------|
| `todaySignIn` | `signin/todaySignIn` | 查询今日签到状态 |
| `userSignIn` | `signin/doUserSignIn` | 执行用户签到 |
| `signInAct` | `signin/signInAcList` | 签到活动列表 |
| `isSign` | `alipay/isSign` | 支付宝签约状态 |
| `unionIsSign` | `unionpay/isSign` | 银联签约状态 |
| `weeklyConDay` | `signin/weeklyConDays` | 周连续签到天数 |
| `checkCaptcha` | `captcha/check` | 验证码校验 |
| `isNeedCaptcha` | `captcha/isNeed` | 是否需要验证码 |
| `queryVersion` | `app/version/query` | 查询版本 |
| `sync` | `data/sync` | 数据同步 |
| `scanV2` | `scan/v2` | 扫码V2 |
| `commonImage` | `common/image` | 通用图片 |

#### 💳 卡片管理 (10个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `cardList` | `card/list` | 卡片列表 |
| `cardDetail` | `card/detail` | 卡片详情 |
| `cardBind` | `card/bind` | 绑定卡片 |
| `cardUnbind` | `card/unbind` | 解绑卡片 |
| `cardDelete` | `card/delete` | 删除卡片 |
| `cardCheck` | `card/check` | 卡片检查 |
| `cardLoss` | `card/loss` | 挂失卡片 |
| `queryCardAccount` | `card/account/query` | 卡账户查询 |
| `campusCardQuotaActive` | `card/campus/quota/active` | 校园卡配额激活 |
| `saveShortNumberAccountPassword` | `card/shortNum/savePwd` | 保存短号密码 |

#### 🎁 其他功能 (31个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `adStatus` | `alipay/tap/adStatus` ✅ | 广告状态 |
| `getAd` | `slot/get` ✅ | 获取广告 |
| `aliYunHitAd` | `aliyun/imarketing/hitAd` ✅ | 阿里云命中广告 |
| `baiduAdTrack` | `task/adTrack` ✅ | 百度广告追踪 |
| `baiduConversion` | `task/baiduConversionCallback` ✅ | 百度转化 |
| `admediaFinishFlag` | `alipay/admedia/finishFlag` ✅ | 广告媒体完成标记 |
| `reportAdAction` | `slot/action/report` ✅ | 上报广告行为 |
| `getAudioFlag` | `config/audio/flag` | 音频标志 |
| `chargeUrl` | `config/charge/url` | 充值URL |
| `cpaDefault` | `config/cpa/default` | CPA默认配置 |
| `ownedByUser` | `user/owned` | 用户拥有 |
| `leaseJoin` | `lease/join` | 租赁加入 |
| `myLeaseGoods` | `lease/my/goods` | 我的租赁商品 |
| `welfareAssistantDetail` | `welfare/assistant/detail` | 福利助手详情 |
| `welfareAssistantEntryCard` | `welfare/assistant/card` | 福利助手入口卡 |
| `icbcShopEligibility` | `shop/icbc/eligibility` | 工行商铺资格 |
| `getThirdChannelToken` | `channel/third/token` | 第三方渠道Token |
| `getVocationList` | `vocation/list` | 假期列表 |
| `uploadFile` | `file/upload` | 上传文件 |
| `uploadFile2` | `file/upload/v2` | 上传文件V2 |
| `uploadFileMuch` | `file/upload/much` | 批量上传 |
| `encryptPhone` | `common/encrypt/phone` | 加密手机号 |
| `sdkResult` | `sdk/result` | SDK结果回调 |
| `communityUserSubmit` | `community/user/submit` | 社区用户提交 |
| `appointNew` | `appoint/new` | 新建预约 |
| `appointAdd` | `appoint/add` | 添加预约 |
| `appointBeforeCheck` | `appoint/before/check` | 预约前检查 |
| `appointCancel` | `appoint/cancel` | 取消预约 |
| `appointOrderDel` | `appoint/order/del` | 删除预约订单 |
| `appointOrderDetails` | `appoint/order/details` | 预约订单详情 |
| `appointSelectTime` | `appoint/select/time` | 选择预约时间 |

---

### 2.2 StarsApi (88 个方法) - 本地生活/社区接口

#### 🏘️ 社区功能 (40个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `communityPost` | `community/post` | 社区发帖 |
| `postList` | `community/post/list` | 帖子列表 |
| `postDetail` | `community/post/detail` | 帖子详情 |
| `postEdit` | `community/post/edit` | 编辑帖子 |
| `postDelete` | `community/post/delete` | 删除帖子 |
| `postTop` | `community/post/top` | 置顶帖子 |
| `postRefresh` | `community/post/refresh` | 刷新帖子 |
| `postExposure` | `community/post/exposure` | 帖子曝光 |
| `postFirstLayer` | `community/post/firstLayer` | 帖子首层评论 |
| `secondLayer` | `community/post/secondLayer` | 二层评论 |
| `postLikeList` | `community/post/like/list` | 点赞列表 |
| `postCommentLike` | `community/comment/like` | 评论点赞 |
| `postCommentLikeCancel` | `community/comment/like/cancel` | 取消评论点赞 |
| `postCommentDelete` | `community/comment/delete` | 删除评论 |
| `sendComment` | `community/comment/send` | 发送评论 |
| `firstComment` | `community/comment/first` | 首条评论 |
| `commentsAndReplies` | `community/comment/replies` | 评论与回复 |
| `setPostCommentSelected` | `community/comment/selected` | 精选评论 |
| `communityLike` | `community/like` | 社区点赞 |
| `communityCancelLike` | `community/like/cancel` | 取消点赞 |
| `likesAndCollects` | `community/likes/collects` | 点赞与收藏 |
| `likeRewardIntegral` | `community/like/reward` | 点赞奖励积分 |
| `communityFollow` | `community/follow` | 关注用户 |
| `unFollow` | `community/unfollow` | 取消关注 |
| `checkFollowed` | `community/follow/check` | 检查关注状态 |
| `communityFollowees` | `community/followees` | 关注列表 |
| `mutualFollowing` | `community/mutual/following` | 互相关注 |
| `newFollowers` | `community/followers/new` | 新粉丝 |
| `communityConcern` | `community/concern` | 社区关注 |
| `communityUserInfo` | `community/user/info` | 社区用户信息 |
| `communityRecommendList` | `community/recommend/list` | 推荐列表 |
| `communityMessageCount` | `community/message/count` | 社区消息数 |
| `communityOpenStatus` | `community/open/status` | 社区开放状态 |
| `communityLifeConfig` | `community/life/config` | 社区生活配置 |
| `getCommunityHomepage` | `community/homepage` | 社区首页 |
| `moments` | `community/moments` | 动态 |
| `searchPost` | `community/search/post` | 搜索帖子 |
| `searchUser` | `community/search/user` | 搜索用户 |
| `searchRecommend` | `community/search/recommend` | 搜索推荐 |
| `getNewPostCount` | `community/post/new/count` | 新帖数量 |

#### 🎯 话题与投票 (10个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `topicDetail` | `topic/detail` | 话题详情 |
| `topicPostList` | `topic/post/list` | 话题帖子列表 |
| `topicRecommendList` | `topic/recommend/list` | 推荐话题 |
| `topicAssociatedList` | `topic/associated/list` | 关联话题 |
| `hotTopic` | `topic/hot` | 热门话题 |
| `voteCommit` | `vote/commit` | 提交投票 |
| `voteResult` | `vote/result` | 投票结果 |
| `voteWhitelistCheck` | `vote/whitelist/check` | 投票白名单检查 |
| `getNotReadCount` | `message/notRead/count` | 未读消息数 |
| `lastContact` | `message/last/contact` | 最后联系 |

#### 🛍️ 社区电商 (15个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `bargainGoods` | `bargain/goods` | 砍价商品 |
| `bargainGroupGoods` | `bargain/group/goods` | 拼团砍价商品 |
| `bargainOrderDetail` | `bargain/order/detail` | 砍价订单详情 |
| `bargainOrderCombineDetail` | `bargain/order/combine/detail` | 组合砍价详情 |
| `createCombine` | `order/combine/create` | 创建组合订单 |
| `updateCombineAddress` | `order/combine/address/update` | 更新组合地址 |
| `createPostOrder` | `order/post/create` | 创建帖子订单 |
| `queryOrder` | `order/query` | 查询订单 |
| `unifyPay` | `pay/unify` | 统一支付 |
| `unusedCoupon` | `coupon/unused` | 未使用优惠券 |
| `couponIssue` | `coupon/issue` | 发放优惠券 |
| `pocketGoodsList` | `goods/pocket/list` | 口袋商品列表 |
| `youzanPocketGoodsList` | `goods/youzan/pocket/list` | 有赞口袋商品 |
| `postGoodSku` | `goods/post/sku` | 帖子商品SKU |
| `postCoin` | `coin/post` | 帖子代币 |

#### 🏫 校园与生活 (12个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `getSchoolHot` | `school/hot` | 校园热门 |
| `querySchoolBySchoolId` | `school/query/byId` | 按ID查学校 |
| `selectSchoolPageList` | `school/page/list` | 学校分页列表 |
| `schoolGetByGoodsId` | `school/get/byGoodsId` | 按商品查学校 |
| `schoolLifeShopDetail` | `school/life/shop/detail` | 校园生活商铺详情 |
| `categoryDetail` | `category/detail` | 分类详情 |
| `listByCategory` | `category/list` | 按分类列表 |
| `deviceRanking` | `ranking/device` | 设备排名 |
| `homeRanking` | `ranking/home` | 首页排名 |
| `coinBalance` | `coin/balance` | 代币余额 |
| `getUserBalance` | `user/balance/get` | 获取用户余额 |
| `latestWithdrawal` | `withdrawal/latest` | 最新提现 |

#### 🔧 其他社区功能 (11个)

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `auditUserInfo` | `user/audit/info` | 审核用户信息 |
| `certifyNotify` | `certify/notify` | 认证通知 |
| `getCertifyId` | `certify/getId` | 获取认证ID |
| `getImToken` | `im/token` | IM Token |
| `pushSetting` | `push/setting` | 推送设置 |
| `pushSettingModify` | `push/setting/modify` | 修改推送设置 |
| `generateShortLink` | `link/short/generate` | 生成短链 |
| `getRrcodeUnlimit` | `qrcode/unlimit` | 无限二维码 |
| `coefficientGetLatestConfig` | `config/coefficient/latest` | 系数最新配置 |
| `incentiveIfOpen` | `incentive/ifOpen` | 激励是否开启 |
| `saveLikeShop` | `shop/like/save` | 保存喜欢的商铺 |
| `uploadFiles2` | `file/upload/v2` | 上传文件V2 |

---

### 2.3 DisApiService (4 个方法) - 分发/排名接口

| 方法名 | 推断路径 | 功能描述 |
|--------|---------|---------|
| `commentConfig` | `dis/comment/config` | 评论配置 |
| `integralRankings` | `dis/integral/rankings` | 积分排名 |
| `mallCategory` | `dis/mall/category` | 商城分类 |
| `rankingHome` | `dis/ranking/home` | 排名首页 |

---

## 三、与 GitHub 开源实现的对比

### 3.1 GitHub 仓库已实现的 13 个接口

| # | GitHub 方法 | 官方 APK 方法 | URL 路径 | 状态 |
|---|------------|--------------|---------|------|
| 1 | `sendCode` | `sendCode` | `common/sms/sendCode` | ✅ 完全匹配 |
| 2 | `login` | `login` | `user/reg` | ✅ 完全匹配 |
| 3 | `queryBalance` | `queryBalance` / `userBalance` | `user/balance` | ✅ 匹配 |
| 4 | `getLatestUsed` | `latestUsed` | `goods/latestUsed` | ✅ 匹配 |
| 5 | `goodsid2sku` | `skus` | `goods/normal/skus` | ✅ 匹配 |
| 6 | `getImei` | `goodsDetails` | `goods/normal/details` | ✅ 匹配 |
| 7 | `useIntergral` | `checkUserIsRisk` | `userIntegral/checkUserIsRisk` | ✅ 匹配 |
| 8 | `addUserAfterPayChannel` | `addAfterPayChannel` | `payChannelRoute/addUserAfterPayChannel` | ✅ 匹配 |
| 9 | `isCheckLocation` | `isCheckLocation` | `orderRisk/isCheckLocation` | ✅ 匹配 |
| 10 | `unlockWater` | `goodsWaterUnlock` | `goods/water/unlock` | ✅ 匹配 |
| 11 | `syncWater` | `waterSync` | `goods/water/sync` | ✅ 匹配 |
| 12 | `createAfterPay` | `afterPayCreate` | `order/afterPay/creating` | ✅ 匹配 |
| 13 | `orderDetail` | `orderDetails` | `order/detail` | ✅ 匹配 |

### 3.2 覆盖率分析

| 维度 | GitHub 实现 | 官方 APK | 覆盖率 |
|------|-----------|---------|--------|
| API 方法数 | 13 | 393 | **3.3%** |
| 用户认证 | 2 | 28 | 7.1% |
| 设备控制 | 3 | 22 | 13.6% |
| 订单管理 | 2 | 32 | 6.3% |
| 支付相关 | 2 | 25 | 8.0% |
| 社区功能 | 0 | 88 | 0% |
| VIP 会员 | 0 | 18 | 0% |
| 积分任务 | 1 | 30 | 3.3% |
| 优惠券 | 0 | 28 | 0% |

---

## 四、关键发现与安全分析

### 4.1 多环境支持

- **生产环境**: `https://userapi.qiekj.com/`
- **本地生活**: 独立 HOST (`LOCAL_LIFE_HOST`)
- **商城**: 独立 HOST (`MALL_HOST_URL`)
- **测试/Mock**: `http://yapi.qiekj.com/mock/11/` (YApi 平台)

### 4.2 安全机制

1. **请求签名**: SHA-256 签名防篡改
2. **Token 认证**: Authorization Header
3. **设备指纹**: deviceId (OAID)
4. **风控签名**: 特定路径需要额外的 orderRiskSign
5. **版本号伪装**: GitHub 仓库使用 `1.59.3`，官方当前版本 `1.144.0`

### 4.3 敏感接口

| 类别 | 高风险接口 | 说明 |
|------|----------|------|
| 支付 | `walletPay`, `alipaySign`, `unionPaySign` | 资金操作 |
| 解锁 | `showerUnlock`, `bleWaterUnlock`, `goodsWaterUnlock` | 设备控制 |
| 绑定 | `aliBind`, `wechatBind`, `cardBind` | 账户关联 |
| 提现 | `withBalance`, `coinRefund` | 资金流出 |
| 实名 | `isNeedRealName`, `certifyNotify` | 身份信息 |

---

## 五、总结

### 5.1 规模统计

| 服务 | 方法数 | 主要功能域 |
|------|-------|----------|
| ApiService | 301 | 核心业务（用户、订单、支付、设备、商品、VIP、积分、优惠券） |
| StarsApi | 88 | 社区/本地生活（帖子、话题、投票、校园、社交） |
| DisApiService | 4 | 分发/排名 |
| **总计** | **393** | - |

### 5.2 GitHub 开源项目定位

GitHub 仓库 (`qiekj-android`) 是一个**极简客户端**，仅实现了设备解锁核心流程（13个接口），覆盖了官方 APK **3.3%** 的 API。它专注于：
- 用户登录/注册
- 余额查询
- 设备解锁（水控/淋浴）
- 订单创建与查询

而官方 APK 是一个**全功能生活服务平台**，包含：
- 完整的电商系统（商品、SKU、订单、支付）
- 社区系统（帖子、评论、关注、话题）
- 会员体系（VIP、积分、任务、优惠券）
- 设备物联网控制（蓝牙解锁、状态同步）
- 多渠道支付（支付宝、微信、银联、钱包）
- 广告投放与追踪
- 校园生活服务

---

*报告生成工具: REA (Reverse Engineering Anything) + JADX*
*分析时间: 2026-10-25*
