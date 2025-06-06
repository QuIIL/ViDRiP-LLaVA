"""
/compuworks/anaconda3/envs/llava/lib/python3.10/site-packages/torch/distributed/run.py
export OMP_NUM_THREADS=8
#export NCCL_IB_DISABLE=0
#export NCCL_IB_GID_INDEX=3
#export NCCL_SOCKET_IFNAME=eth0
export NCCL_DEBUG=INFO

#export NCCL_P2P_DISABLE=1
#export NCCL_SHM_DISABLE=1


LLM_VERSION="/data1/trinh/code/ViLa/video/LLaVA-NeXT/hf_weight/Qwen/Qwen2.5-0.5B-Instruct"
#LLM_VERSION="Qwen/Qwen2-0.5B-Instruct"

#LLM_VERSION_CLEAN="${LLM_VERSION//\//_}"
LLM_VERSION_CLEAN=$(basename "$LLM_VERSION")

VISION_MODEL_VERSION="google/siglip-so400m-patch14-384"
#VISION_MODEL_VERSION_CLEAN="${VISION_MODEL_VERSION//\//_}"
VISION_MODEL_VERSION_CLEAN="siglip"


############### my input ################
NNODES=1
RANK=0
PORT=25052
NUM_GPUS=4
export CUDA_VISIBLE_DEVICES=4,5,6,7
export ADDR="127.0.0.1"  # or another valid IP address/hostname
echo "MASTER_ADDR="$ADDR
############### Pretrain ################

BASE_RUN_NAME="llavanext-${VISION_MODEL_VERSION_CLEAN}-Qwen2.5-0.5B-Instruct-mlp2x_gelu-pretrain_PathResVL_pretrain"
echo "BASE_RUN_NAME: ${BASE_RUN_NAME}"

############### Finetune ################

# Stage 2
PROMPT_VERSION="qwen_1_5"
RUN_NAME="llava-onevision-${VISION_MODEL_VERSION_CLEAN}-${LLM_VERSION_CLEAN}-ov_PathResVL_instruct_2dms"
#PREV_STAGE_CHECKPOINT="/mnt/bn/vl-research/checkpoints/onevision/llavanext-google_siglip-so400m-patch14-384-Qwen_Qwen2-7B-Instruct-mid_to_final_next_3m_am9_july14" # replace it with your last checkpoint training from single image collection
PREV_STAGE_CHECKPOINT="/data1/trinh/code/ViLa/video/LLaVA-NeXT/checkpoints/llavanext-siglip-Qwen2.5-0.5B-Instruct-mlp2x_gelu-pretrain_PathResVL_2dms_instruct" # replace it with your last checkpoint training from single image collection
echo "PREV_STAGE_CHECKPOINT: ${PREV_STAGE_CHECKPOINT}"
echo "MID_RUN_NAME: ${RUN_NAME}"

ACCELERATE_CPU_AFFINITY=1 torchrun --nproc_per_node=1 --nnodes=1 --node_rank=0 --master_addr="127.0.0.1"  --master_port=25053


--nproc_per_node=1
    llava/train/train_mem.py
    --deepspeed scripts/zero3_debug.json
    --model_name_or_path "/data1/trinh/code/ViLa/video/LLaVA-NeXT/checkpoints/llavanext-siglip-Qwen2.5-0.5B-Instruct-mlp2x_gelu-pretrain_PathResVL_2dms_instruct"
    --version "qwen_1_5"
    --data_path /data1/trinh/code/ViLa/video/LLaVA-NeXT/scripts/train/onevision_si.yaml
    --image_folder /ssd1/trinh/data/ViLa/images/
    --video_folder /data1/trinh/data/raw_data/quilt1m_data/clips_histo_frame
    --mm_tunable_parts="mm_vision_tower,mm_mlp_adapter,mm_language_model"
    --mm_vision_tower_lr=2e-6
    --vision_tower "google/siglip-so400m-patch14-384"
    --mm_projector_type mlp2x_gelu
    --mm_vision_select_layer -2
    --mm_use_im_start_end False
    --mm_use_im_patch_token False
    --group_by_modality_length True
    --image_aspect_ratio anyres
    --image_grid_pinpoints "[(384, 384), (384, 768), (768, 384), (768, 768), (1152, 384), (384, 1152)]"
    --video_center_crop 0.5
    --mm_patch_merge_type spatial_unpad
    --bf16 True
    --run_name $RUN_NAME
    --output_dir ./checkpoints/onevision/llava-onevision-Qwen2-0.5B-Instruct-siglip-ov_PathResVL_instruct_2dms
    --num_train_epochs 1
    --per_device_train_batch_size 2
    --per_device_eval_batch_size 4
    --gradient_accumulation_steps 2
    --evaluation_strategy "no"
    --save_strategy "steps"
    --save_steps 1000
    --save_total_limit 1
    --learning_rate 1e-5
    --weight_decay 0.
    --warmup_ratio 0.03
    --lr_scheduler_type "cosine"
    --logging_steps 1
    --tf32 True
    --model_max_length 32768
    --gradient_checkpointing True
    --dataloader_num_workers 4
    --lazy_preprocess True
    --report_to wandb
    --torch_compile True
    --torch_compile_backend "inductor"
    --dataloader_drop_last True
    --frames_upbound 32
exit 0;


--nproc_per_node=1 --nnodes=1 --node_rank=0 --master_addr="127.0.0.1"  --master_port=25053     llava/train/train_mem.py     --deepspeed scripts/zero3.json     --model_name_or_path "/data1/trinh/code/ViLa/video/LLaVA-NeXT/checkpoints/llavanext-siglip-Qwen2.5-0.5B-Instruct-mlp2x_gelu-pretrain_PathResVL_2dms_instruct"     --version "qwen_1_5"     --data_path /data1/trinh/code/ViLa/video/LLaVA-NeXT/scripts/train/onevision.yaml     --image_folder /ssd1/trinh/data/ViLa/images/     --video_folder /data1/trinh/data/raw_data/quilt1m_data/clips_histo_frame     --mm_tunable_parts="mm_vision_tower,mm_mlp_adapter,mm_language_model"     --mm_vision_tower_lr=2e-6     --vision_tower "google/siglip-so400m-patch14-384"     --mm_projector_type mlp2x_gelu     --mm_vision_select_layer -2     --mm_use_im_start_end False     --mm_use_im_patch_token False     --group_by_modality_length True     --image_aspect_ratio anyres_max_9     --image_grid_pinpoints  "(1x1),...,(6x6)"     --mm_patch_merge_type spatial_unpad     --bf16 True     --run_name dump     --output_dir ./checkpoints/onevision/llava-onevision-Qwen2-0.5B-Instruct-siglip-ov_PathResVL_instruct_2dms_dump     --num_train_epochs 1     --per_device_train_batch_size 2     --per_device_eval_batch_size 4      --gradient_accumulation_steps 2     --evaluation_strategy "no"     --save_strategy "steps"     --save_steps 1000     --save_total_limit 1     --learning_rate 1e-5     --weight_decay 0.     --warmup_ratio 0.03     --lr_scheduler_type "cosine"     --logging_steps 1     --tf32 True     --model_max_length 32768     --gradient_checkpointing True     --dataloader_num_workers 4     --lazy_preprocess True     --report_to wandb     --torch_compile True     --torch_compile_backend "inductor"     --dataloader_drop_last True     --frames_upbound 32

20700
37239
69777


2. Add Environment Variables:
You can specify the GPU using environment variables or command-line arguments.

Option 1: Using Environment Variables
In the Edit Configurations window, choose the configuration you want to modify (e.g., your script).
Scroll down to the Environment section, and find Environment variables.
Click on the ... button next to Environment variables.
Add the environment variable to specify the GPU device. For example:
For TensorFlow: CUDA_VISIBLE_DEVICES=0 (to use GPU 0).
For PyTorch: CUDA_DEVICE_ORDER=PCI_BUS_ID and CUDA_VISIBLE_DEVICES=0.
"""
