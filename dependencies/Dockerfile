FROM continuumio/miniconda3
SHELL ["/bin/bash", "--login", "-c"]

WORKDIR /opt
RUN source /opt/conda/etc/profile.d/conda.sh && \
    # add bioformats2raw
    conda create --yes --name bf2raw python=3.9 && \
    conda install -n bf2raw -c "ome/label/pre" bioformats2raw && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate bf2raw\nbioformats2raw $@' >> /usr/local/bin/bioformats2raw && \
    chmod 777 /usr/local/bin/bioformats2raw && \
    # add bftools
    conda create --yes --name bioformats python=3.9 && \
    conda install -n bioformats -c "ome" bftools && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate bioformats\nbfconvert $@' >> /usr/local/bin/bfconvert && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate bioformats\ntiffcomment $@' >> /usr/local/bin/tiffcomment && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate bioformats\nshowinf -nopix $@' >> /usr/local/bin/showinf && \
    chmod 777 /usr/local/bin/bfconvert && \
    chmod 777 /usr/local/bin/tiffcomment && \
    chmod 777 /usr/local/bin/showinf && \
    ### todo: add access to other bftools commands
    # add minio-client
    conda create --yes --name mc python=3.9 && \
    conda install -n mc -c joshmoore go-mc && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate mc\nmc $@' >> /usr/local/bin/mc && \
    chmod 777 /usr/local/bin/mc && \
    # add ascp
    conda create --yes --name ascp2bia python=3.9 && \
    conda install -n ascp2bia -c hcc aspera-cli && \
    echo $'#!/usr/bin/env -S bash --noprofile --norc' >> /usr/local/bin/ascp && \
    echo 'source /opt/conda/etc/profile.d/conda.sh;' >> /usr/local/bin/ascp && \
    echo 'conda activate ascp2bia' >> /usr/local/bin/ascp && \
    echo 'ascp $@' >> /usr/local/bin/ascp && \
    ####
    echo $'#!/usr/bin/env -S bash --noprofile --norc' >> /usr/local/bin/fast2bia && \
    echo 'source /opt/conda/etc/profile.d/conda.sh;' >> /usr/local/bin/fast2bia && \
    echo 'conda activate ascp2bia' >> /usr/local/bin/fast2bia && \
    echo 'ascp -P33001 -l 500M -k 2 -i $SSH_KEY -d $1 bsaspera_w@hx-fasp-1.ebi.ac.uk:$2' >> /usr/local/bin/fast2bia && \
    chmod -R 777 /usr/local/bin
    ### todo: add to this also fast2local
