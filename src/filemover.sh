# 1. Define paths correctly
TRAINING_TARGETS="/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/train"
VALIDATION_TARGETS="/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/val"

TRAINING_LABELS="/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/autoannotatelogs/Run1_training/labels"
VALIDATION_LABELS="/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/autoannotatelogs/Run1_validation/labels"

# 2. Move the CONTENTS (/*) into the target destinations
mv "$TRAINING_LABELS"/* "$TRAINING_TARGETS"/
mv "$VALIDATION_LABELS"/* "$VALIDATION_TARGETS"/


